from fastapi.testclient import TestClient

from app.main import app
from app.services.process_service import InMemoryJobStore, ProcessingService, get_processing_service

client = TestClient(app)


def _override_service():
    """Give each test an isolated job store so tests don't leak state into each other."""
    service = ProcessingService(store=InMemoryJobStore())
    app.dependency_overrides[get_processing_service] = lambda: service
    return service


def teardown_function() -> None:
    app.dependency_overrides.pop(get_processing_service, None)


def test_create_process_job_success():
    _override_service()
    response = client.post(
        "/api/v1/process",
        json={
            "project_id": "project-001",
            "dataset_id": "dataset-001",
            "features": ["parcels", "buildings"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    assert "job_id" in body and body["job_id"]


def test_create_process_job_missing_project_id():
    _override_service()
    response = client.post(
        "/api/v1/process",
        json={"dataset_id": "dataset-001", "features": ["parcels"]},
    )
    assert response.status_code == 422


def test_create_process_job_missing_dataset_id():
    _override_service()
    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "features": ["parcels"]},
    )
    assert response.status_code == 422


def test_create_process_job_empty_features():
    _override_service()
    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": []},
    )
    assert response.status_code == 422


def test_create_process_job_unsupported_feature():
    _override_service()
    response = client.post(
        "/api/v1/process",
        json={
            "project_id": "project-001",
            "dataset_id": "dataset-001",
            "features": ["parcels", "flying_cars"],
        },
    )
    assert response.status_code == 422


def test_create_process_job_invalid_feature_type():
    _override_service()
    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": [123]},
    )
    assert response.status_code == 422


def test_job_status_retrieval():
    _override_service()
    create_response = client.post(
        "/api/v1/process",
        json={
            "project_id": "project-001",
            "dataset_id": "dataset-001",
            "features": ["roads"],
        },
    )
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/v1/process/{job_id}")
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["job_id"] == job_id
    assert body["status"] == "queued"


def test_job_not_found():
    _override_service()
    response = client.get("/api/v1/process/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_job_ids_are_unique():
    _override_service()
    ids = set()
    for _ in range(5):
        response = client.post(
            "/api/v1/process",
            json={
                "project_id": "project-001",
                "dataset_id": "dataset-001",
                "features": ["land_use"],
            },
        )
        ids.add(response.json()["job_id"])
    assert len(ids) == 5
