from fastapi.testclient import TestClient

from app.main import app
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
