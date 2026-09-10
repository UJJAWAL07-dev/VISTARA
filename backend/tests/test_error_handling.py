"""
Phase 6: tests for the global unhandled-exception handler registered in
app/main.py, and confirmation that existing HTTPException (404) and
Pydantic validation (422) behavior is unaffected by adding it.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.services.project_service import InMemoryProjectStore, ProjectService, get_project_service

client = TestClient(app)


class BrokenProjectService:
    """
    Test double simulating a genuine, unexpected bug - something that
    isn't one of the domain errors (like ProjectNotFoundError) any
    service already catches and translates into a specific HTTPException.
    Deliberately does NOT subclass ProjectService: FastAPI's Depends()
    doesn't check the returned object's type against the route's type
    hint, it only calls whatever's registered and uses the result, so a
    minimal stand-in exposing just the method the route calls is enough.
    """

    def list_projects(self):
        raise RuntimeError("boom - simulated unexpected failure for testing")


def teardown_function() -> None:
    app.dependency_overrides.pop(get_project_service, None)


def test_unhandled_exception_returns_safe_generic_500():
    app.dependency_overrides[get_project_service] = lambda: BrokenProjectService()

    # Starlette's ServerErrorMiddleware always re-raises the original
    # exception after sending the generated response - intentional, so
    # bugs surface loudly in dev/test tooling. TestClient's default
    # raise_server_exceptions=True then re-raises that same exception in
    # the test process itself, even though a real client (or uvicorn in
    # production) would have already received the safe response over the
    # wire. A client with raise_server_exceptions=False is the standard
    # way to assert the response itself in a test; scoped to just this
    # test so bugs in other tests still surface normally.
    non_raising_client = TestClient(app, raise_server_exceptions=False)
    response = non_raising_client.get("/api/v1/projects")

    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected internal error occurred."}
    # Never leak the real exception type, message, or a traceback to the client.
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
    assert "boom" not in response.text


def test_existing_404_behavior_is_unaffected():
    service = ProjectService(store=InMemoryProjectStore())
    app.dependency_overrides[get_project_service] = lambda: service

    response = client.get("/api/v1/projects/does-not-exist")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_existing_422_validation_behavior_is_unaffected():
    service = ProjectService(store=InMemoryProjectStore())
    app.dependency_overrides[get_project_service] = lambda: service

    response = client.post("/api/v1/projects", json={"description": "missing required name"})

    assert response.status_code == 422
