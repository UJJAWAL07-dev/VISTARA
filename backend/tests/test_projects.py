from fastapi.testclient import TestClient

from app.main import app
from app.services.dataset_service import DatasetService, InMemoryDatasetStore, get_dataset_service
from app.services.project_service import InMemoryProjectStore, ProjectService, get_project_service

client = TestClient(app)


def _fresh_service() -> ProjectService:
    """Give each test an isolated store so tests don't leak state into each other."""
    return ProjectService(store=InMemoryProjectStore())


def _override_service():
    service = _fresh_service()
    app.dependency_overrides[get_project_service] = lambda: service
    return service


def teardown_function() -> None:
    app.dependency_overrides.pop(get_project_service, None)
    app.dependency_overrides.pop(get_dataset_service, None)


def test_create_project():
    _override_service()
    response = client.post(
        "/api/v1/projects",
        json={"name": "Coastal Erosion Survey", "description": "Phase 1 pilot"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Coastal Erosion Survey"
    assert body["status"] == "active"
    assert "id" in body
    assert "created_at" in body


def test_create_project_requires_name():
    _override_service()
    response = client.post("/api/v1/projects", json={"description": "missing name"})
    assert response.status_code == 422


def test_list_projects():
    _override_service()
    client.post("/api/v1/projects", json={"name": "Project A"})
    client.post("/api/v1/projects", json={"name": "Project B"})

    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_get_project():
    _override_service()
    create_response = client.post("/api/v1/projects", json={"name": "Project A"})
    project_id = create_response.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_get_project_not_found():
    _override_service()
    response = client.get("/api/v1/projects/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_update_project():
    _override_service()
    create_response = client.post("/api/v1/projects", json={"name": "Original Name"})
    project_id = create_response.json()["id"]

    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Name", "status": "archived"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Updated Name"
    assert body["status"] == "archived"


def test_update_project_not_found():
    _override_service()
    response = client.put("/api/v1/projects/does-not-exist", json={"name": "New Name"})
    assert response.status_code == 404


def test_delete_project():
    _override_service()
    create_response = client.post("/api/v1/projects", json={"name": "To Delete"})
    project_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/projects/{project_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 404


def test_delete_project_not_found():
    _override_service()
    response = client.delete("/api/v1/projects/does-not-exist")
    assert response.status_code == 404


def _override_project_and_dataset_services():
    """
    Phase 6: wires an isolated ProjectService and DatasetService together
    so a project's cascade-delete calls into THIS test's dataset store,
    not the real production DatasetService singleton. Each service needs
    a callable pointing at the other (dataset_cleanup / project_lookup);
    since the callables are only invoked later (not at construction time),
    Python's closures let the two lambdas below reference each other's
    enclosing-scope variable regardless of which is defined first.
    """
    project_service = ProjectService(
        store=InMemoryProjectStore(),
        dataset_cleanup=lambda project_id: dataset_service.delete_by_project(project_id),
    )
    dataset_service = DatasetService(
        store=InMemoryDatasetStore(),
        project_lookup=lambda project_id: project_service.get_project(project_id),
    )
    app.dependency_overrides[get_project_service] = lambda: project_service
    app.dependency_overrides[get_dataset_service] = lambda: dataset_service
    return project_service, dataset_service


def test_deleting_project_cascades_to_its_datasets():
    _override_project_and_dataset_services()

    # Project with two datasets, and an unrelated second project with one
    # dataset - the cascade must only touch the deleted project's own data.
    target_project_id = client.post("/api/v1/projects", json={"name": "Target Project"}).json()["id"]
    other_project_id = client.post("/api/v1/projects", json={"name": "Other Project"}).json()["id"]

    dataset_1_id = client.post(
        "/api/v1/datasets",
        json={"project_id": target_project_id, "name": "Dataset 1", "dataset_type": "csv"},
    ).json()["id"]
    dataset_2_id = client.post(
        "/api/v1/datasets",
        json={"project_id": target_project_id, "name": "Dataset 2", "dataset_type": "geojson"},
    ).json()["id"]
    other_dataset_id = client.post(
        "/api/v1/datasets",
        json={"project_id": other_project_id, "name": "Unrelated Dataset", "dataset_type": "csv"},
    ).json()["id"]

    delete_response = client.delete(f"/api/v1/projects/{target_project_id}")
    assert delete_response.status_code == 204

    # The deleted project's own datasets are gone.
    assert client.get(f"/api/v1/datasets/{dataset_1_id}").status_code == 404
    assert client.get(f"/api/v1/datasets/{dataset_2_id}").status_code == 404

    # The unrelated project and its dataset are untouched.
    assert client.get(f"/api/v1/projects/{other_project_id}").status_code == 200
    assert client.get(f"/api/v1/datasets/{other_dataset_id}").status_code == 200


def test_deleting_project_with_no_datasets_succeeds():
    """Cascade delete must be a safe no-op when there's nothing to clean up."""
    _override_project_and_dataset_services()

    project_id = client.post("/api/v1/projects", json={"name": "Empty Project"}).json()["id"]

    delete_response = client.delete(f"/api/v1/projects/{project_id}")
    assert delete_response.status_code == 204
