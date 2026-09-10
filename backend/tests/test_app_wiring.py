"""
Phase 8: application wiring tests.

These tests don't exercise any single feature's business logic (that's
what test_projects.py / test_datasets.py / test_process.py are for).
Instead they confirm the FastAPI app itself is correctly assembled -
that every router got included, that the OpenAPI schema actually
generates, and that the interactive docs UI is reachable. A test suite
made entirely of per-feature tests would never catch a mistake like
"someone forgot to add a new router to api_v1_router" - these tests
close that gap.

Note: the real path parameter names registered in the OpenAPI schema
are {project_id}, {dataset_id}, and {job_id} - not a generic {id} -
matching exactly what each route decorator in app/routes/*.py declares.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# (path, method) pairs expected to exist in the generated OpenAPI schema.
# Method names are lowercase to match how OpenAPI documents them.
EXPECTED_PATHS_AND_METHODS = {
    ("/api/v1/health", "get"),
    ("/api/v1/projects", "post"),
    ("/api/v1/projects", "get"),
    ("/api/v1/projects/{project_id}", "get"),
    ("/api/v1/projects/{project_id}", "put"),
    ("/api/v1/projects/{project_id}", "delete"),
    ("/api/v1/datasets", "post"),
    ("/api/v1/datasets", "get"),
    ("/api/v1/datasets/{dataset_id}", "get"),
    ("/api/v1/datasets/{dataset_id}", "put"),
    ("/api/v1/datasets/{dataset_id}", "delete"),
    ("/api/v1/process", "post"),
    ("/api/v1/process", "get"),
    ("/api/v1/process/{job_id}", "get"),
}


def test_openapi_schema_generates_successfully():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    assert isinstance(schema, dict)
    assert "paths" in schema
    assert isinstance(schema["paths"], dict)


def test_all_expected_paths_are_registered():
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    registered = set()
    for path, operations in paths.items():
        for method in operations:
            # OpenAPI's per-path dict can include non-method keys (e.g.
            # "parameters" for path-level params); only method names are
            # actual HTTP operations, so filter to the ones we care about.
            if method in {"get", "post", "put", "delete", "patch"}:
                registered.add((path, method))

    missing = EXPECTED_PATHS_AND_METHODS - registered
    assert not missing, f"Expected path/method pairs missing from OpenAPI schema: {missing}"


def test_docs_ui_is_reachable():
    response = client.get("/docs")

    assert response.status_code == 200
