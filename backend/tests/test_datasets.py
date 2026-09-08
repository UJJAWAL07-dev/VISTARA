from fastapi.testclient import TestClient

from app.main import app
from app.services.dataset_service import DatasetService, InMemoryDatasetStore, get_dataset_service
from app.services.project_service import InMemoryProjectStore, ProjectService, get_project_service

client = TestClient(app)


def _override_services():
    """
    Give each test isolated project + dataset stores so tests don't leak
    state into each other, and so the dataset service validates against
    the same fresh project store the test creates projects in.
    """
    project_service = ProjectService(store=InMemoryProjectStore())
    dataset_service = DatasetService(
        store=InMemoryDatasetStore(),
        project_lookup=project_service.get_project,
    )
    app.dependency_overrides[get_project_service] = lambda: project_service
    app.dependency_overrides[get_dataset_service] = lambda: dataset_service
    return project_service, dataset_service


def teardown_function() -> None:
    app.dependency_overrides.pop(get_project_service, None)
    app.dependency_overrides.pop(get_dataset_service, None)


def _create_project() -> str:
    response = client.post("/api/v1/projects", json={"name": "Coastal Erosion Survey"})
    return response.json()["id"]


def test_create_dataset():
    _override_services()
    project_id = _create_project()

    response = client.post(
        "/api/v1/datasets",
        json={"project_id": project_id, "name": "Shoreline 2024", "dataset_type": "geojson"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert body["name"] == "Shoreline 2024"
    assert body["dataset_type"] == "geojson"
    assert body["status"] == "registered"


def test_create_dataset_requires_existing_project():
    _override_services()
    response = client.post(
        "/api/v1/datasets",
        json={"project_id": "does-not-exist", "name": "Orphan Dataset", "dataset_type": "csv"},
    )
    assert response.status_code == 404


def test_create_dataset_requires_name_and_type():
    _override_services()
    project_id = _create_project()
    response = client.post("/api/v1/datasets", json={"project_id": project_id})
    assert response.status_code == 422


def test_list_datasets_filtered_by_project():
    _override_services()
    project_a = _create_project()
    project_b_response = client.post("/api/v1/projects", json={"name": "Project B"})
    project_b = project_b_response.json()["id"]

    client.post(
        "/api/v1/datasets",
        json={"project_id": project_a, "name": "A1", "dataset_type": "csv"},
    )
    client.post(
        "/api/v1/datasets",
        json={"project_id": project_b, "name": "B1", "dataset_type": "csv"},
    )

    response = client.get(f"/api/v1/datasets?project_id={project_a}")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["project_id"] == project_a


def test_get_dataset():
    _override_services()
    project_id = _create_project()
    create_response = client.post(
        "/api/v1/datasets",
        json={"project_id": project_id, "name": "Dataset", "dataset_type": "csv"},
    )
    dataset_id = create_response.json()["id"]

    response = client.get(f"/api/v1/datasets/{dataset_id}")
    assert response.status_code == 200
    assert response.json()["id"] == dataset_id


def test_get_dataset_not_found():
    _override_services()
    response = client.get("/api/v1/datasets/does-not-exist")
    assert response.status_code == 404


def test_update_dataset():
    _override_services()
    project_id = _create_project()
    create_response = client.post(
        "/api/v1/datasets",
        json={"project_id": project_id, "name": "Original", "dataset_type": "csv"},
    )
    dataset_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/datasets/{dataset_id}",
        json={"name": "Renamed", "status": "processed"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Renamed"
    assert body["status"] == "processed"


def test_update_dataset_not_found():
    _override_services()
    response = client.put("/api/v1/datasets/does-not-exist", json={"name": "New Name"})
    assert response.status_code == 404


def test_delete_dataset():
    _override_services()
    project_id = _create_project()
    create_response = client.post(
        "/api/v1/datasets",
        json={"project_id": project_id, "name": "To Delete", "dataset_type": "csv"},
    )
    dataset_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/datasets/{dataset_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/datasets/{dataset_id}")
    assert get_response.status_code == 404


def test_delete_dataset_not_found():
    _override_services()
    response = client.delete("/api/v1/datasets/does-not-exist")
    assert response.status_code == 404
