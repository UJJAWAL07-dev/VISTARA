from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

from app.integrations.ai_adapter import AIAdapter, AIAdapterError
from app.integrations.analysis_adapter import AnalysisAdapter
from app.integrations.gis_adapter import GISAdapter
from app.main import app
from app.models.job import Job
from app.services.dataset_service import DatasetService, InMemoryDatasetStore, get_dataset_service
from app.services.process_service import InMemoryJobStore, ProcessingService, get_processing_service
from app.services.project_service import InMemoryProjectStore, ProjectService, get_project_service

client = TestClient(app)


class RecordingJobStore(InMemoryJobStore):
    """
    Test double that records every status a job passes through, so tests
    can confirm the job actually moved through "processing" on its way to
    "completed"/"failed", not just that it ended up somewhere.
    """

    def __init__(self) -> None:
        super().__init__()
        self.status_history: List[str] = []

    def add(self, job: Job) -> Job:
        self.status_history.append(job.status)
        return super().add(job)

    def update(self, job_id: str, job: Job) -> Optional[Job]:
        self.status_history.append(job.status)
        return super().update(job_id, job)


class FailingAIAdapter(AIAdapter):
    """Test double that always raises, to exercise the failure path."""

    def run_inference(self, job: Any) -> Dict[str, Any]:
        raise AIAdapterError("mock AI failure for testing")


class MalformedAIAdapter(AIAdapter):
    """
    Phase 7: test double that returns successfully but with output that
    does NOT match GeoJSONFeatureCollection (missing the required
    "features" key) - simulating a real adapter that doesn't (yet)
    conform to the documented contract, rather than one that raises.
    """

    def run_inference(self, job: Any) -> Dict[str, Any]:
        return {"type": "FeatureCollection"}  # missing required "features"


class MalformedGISAdapter(GISAdapter):
    """Returns output missing GISResult's required "feature_count" field."""

    def process(self, job: Any, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        return {"layer_id": "layer-x", "name": "Bad Layer", "crs": "EPSG:4326", "geojson": ai_result}


class MalformedAnalysisAdapter(AnalysisAdapter):
    """Returns output missing AnalysisResult's required "validation" field."""

    def analyze(self, job: Any, gis_result: Dict[str, Any]) -> Dict[str, Any]:
        return {"statistics": {"feature_count": 0}, "issues": []}


def _override_all_services(
    job_store: Optional[InMemoryJobStore] = None,
    ai_adapter: Optional[AIAdapter] = None,
    gis_adapter: Optional[GISAdapter] = None,
    analysis_adapter: Optional[AnalysisAdapter] = None,
):
    """
    Phase 9: wires isolated Project, Dataset, and Processing services
    together so a test's process-job creation validates its project_id/
    dataset_id against the SAME in-memory stores the test's own
    /api/v1/projects and /api/v1/datasets calls use - not the real
    production singletons. Mirrors the same pattern already used in
    tests/test_projects.py for cascade-delete testing (an isolated
    ProjectService/DatasetService pair, wired via the same public
    lookup methods ProcessingService injects by default in production).

    Returns (project_service, dataset_service, processing_service) so a
    test can also assert directly on ProcessingService's own state (e.g.
    that no job was created) without needing a second HTTP round trip.
    """
    project_service = ProjectService(store=InMemoryProjectStore())
    dataset_service = DatasetService(
        store=InMemoryDatasetStore(),
        project_lookup=project_service.get_project,
    )
    processing_service = ProcessingService(
        store=job_store or InMemoryJobStore(),
        ai_adapter=ai_adapter,
        gis_adapter=gis_adapter,
        analysis_adapter=analysis_adapter,
        project_lookup=project_service.get_project,
        dataset_lookup=dataset_service.get_dataset,
    )

    app.dependency_overrides[get_project_service] = lambda: project_service
    app.dependency_overrides[get_dataset_service] = lambda: dataset_service
    app.dependency_overrides[get_processing_service] = lambda: processing_service

    return project_service, dataset_service, processing_service


def _create_project_and_dataset(dataset_type: str = "csv") -> tuple:
    """
    Creates a real project and a real dataset under it via the actual
    API, returning (project_id, dataset_id). Used so process-job tests
    submit against real, existing records rather than fabricated IDs -
    required since Phase 9 validates both actually exist.
    """
    project_id = client.post("/api/v1/projects", json={"name": "Test Project"}).json()["id"]
    dataset_id = client.post(
        "/api/v1/datasets",
        json={"project_id": project_id, "name": "Test Dataset", "dataset_type": dataset_type},
    ).json()["id"]
    return project_id, dataset_id


def teardown_function() -> None:
    app.dependency_overrides.pop(get_project_service, None)
    app.dependency_overrides.pop(get_dataset_service, None)
    app.dependency_overrides.pop(get_processing_service, None)


def test_create_process_job_success():
    _override_all_services()
    project_id, dataset_id = _create_project_and_dataset()

    response = client.post(
        "/api/v1/process",
        json={
            "project_id": project_id,
            "dataset_id": dataset_id,
            "features": ["parcels", "buildings"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    # Phase 4: orchestration is synchronous, so by the time POST returns,
    # the (mocked) pipeline has already finished successfully.
    assert body["status"] == "completed"
    assert "job_id" in body and body["job_id"]


def test_create_process_job_missing_project_id():
    _override_all_services()
    # Missing field entirely -> rejected by Pydantic before the service
    # layer (and its existence checks) ever runs, so a fabricated
    # dataset_id here is fine - it's never actually looked up.
    response = client.post(
        "/api/v1/process",
        json={"dataset_id": "dataset-001", "features": ["parcels"]},
    )
    assert response.status_code == 422


def test_create_process_job_missing_dataset_id():
    _override_all_services()
    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "features": ["parcels"]},
    )
    assert response.status_code == 422


def test_create_process_job_empty_features():
    _override_all_services()
    # Rejected by Pydantic's min_length=1 on `features` before the
    # service layer runs - fabricated IDs are fine, never looked up.
    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": []},
    )
    assert response.status_code == 422


def test_create_process_job_unsupported_feature():
    _override_all_services()
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
    _override_all_services()
    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": [123]},
    )
    assert response.status_code == 422


def test_create_process_job_requires_existing_project():
    """Phase 9: a nonexistent project_id must 404, and must not create a Job."""
    _, _, processing_service = _override_all_services()

    response = client.post(
        "/api/v1/process",
        json={
            "project_id": "does-not-exist",
            "dataset_id": "also-does-not-exist",
            "features": ["parcels"],
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 'does-not-exist' not found"
    # No Job should have been created as a side effect of the failed attempt.
    assert processing_service.list_jobs() == []


def test_create_process_job_requires_existing_dataset():
    """Phase 9: a valid project but a nonexistent dataset_id must 404,
    and must not create a Job."""
    _, _, processing_service = _override_all_services()
    project_id = client.post("/api/v1/projects", json={"name": "Real Project"}).json()["id"]

    response = client.post(
        "/api/v1/process",
        json={
            "project_id": project_id,
            "dataset_id": "does-not-exist",
            "features": ["parcels"],
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Dataset 'does-not-exist' not found"
    assert processing_service.list_jobs() == []


def test_job_status_retrieval():
    _override_all_services()
    project_id, dataset_id = _create_project_and_dataset()

    create_response = client.post(
        "/api/v1/process",
        json={"project_id": project_id, "dataset_id": dataset_id, "features": ["roads"]},
    )
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/v1/process/{job_id}")
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["job_id"] == job_id
    # Phase 4: same reasoning as test_create_process_job_success - the mocked
    # pipeline has already completed by the time this job exists at all.
    assert body["status"] == "completed"


def test_job_not_found():
    _override_all_services()
    response = client.get("/api/v1/process/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_job_ids_are_unique():
    _override_all_services()
    project_id, dataset_id = _create_project_and_dataset()

    ids = set()
    for _ in range(5):
        response = client.post(
            "/api/v1/process",
            json={"project_id": project_id, "dataset_id": dataset_id, "features": ["land_use"]},
        )
        ids.add(response.json()["job_id"])
    assert len(ids) == 5


def test_pipeline_progresses_through_processing_before_completed():
    """Phase 4: confirms the job actually passes through 'processing',
    not just that it ends at 'completed' - using a store that records
    every status transition it observes."""
    store = RecordingJobStore()
    _override_all_services(job_store=store)
    project_id, dataset_id = _create_project_and_dataset()

    response = client.post(
        "/api/v1/process",
        json={"project_id": project_id, "dataset_id": dataset_id, "features": ["parcels"]},
    )
    assert response.status_code == 201

    assert "processing" in store.status_history
    assert store.status_history.index("processing") < store.status_history.index("completed")


def test_completed_job_contains_ai_gis_and_analysis_result():
    _override_all_services()
    project_id, dataset_id = _create_project_and_dataset()

    create_response = client.post(
        "/api/v1/process",
        json={
            "project_id": project_id,
            "dataset_id": dataset_id,
            "features": ["parcels", "buildings", "roads", "land_use"],
        },
    )
    job_id = create_response.json()["job_id"]

    status_response = client.get(f"/api/v1/process/{job_id}")
    assert status_response.status_code == 200
    body = status_response.json()

    assert body["status"] == "completed"
    assert body["error"] is None

    result = body["result"]
    assert result is not None

    # AI stage: GeoJSON FeatureCollection with one feature per requested type.
    assert result["ai"]["type"] == "FeatureCollection"
    assert len(result["ai"]["features"]) == 4

    # GIS stage: normalized layer wrapping the AI output.
    gis = result["gis"]
    assert gis["feature_count"] == 4
    assert gis["crs"] == "EPSG:4326"
    assert gis["geojson"]["type"] == "FeatureCollection"

    # Analysis stage: statistics/issues/validation structure.
    analysis = result["analysis"]
    assert analysis["statistics"]["feature_count"] == 4
    assert analysis["statistics"]["building_count"] == 1
    assert analysis["statistics"]["parcel_count"] == 1
    assert analysis["validation"]["status"] == "valid"
    assert analysis["issues"] == []


def test_adapter_failure_marks_job_failed_with_safe_error():
    _override_all_services(ai_adapter=FailingAIAdapter())
    project_id, dataset_id = _create_project_and_dataset()

    response = client.post(
        "/api/v1/process",
        json={"project_id": project_id, "dataset_id": dataset_id, "features": ["parcels"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"

    status_response = client.get(f"/api/v1/process/{body['job_id']}")
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["status"] == "failed"
    assert status_body["result"] is None
    assert status_body["error"] == "mock AI failure for testing"
    # Safe error only - no traceback content (no "Traceback", no file paths).
    assert "Traceback" not in status_body["error"]
    assert ".py" not in status_body["error"]


def test_list_process_jobs_returns_empty_when_none_exist():
    _override_all_services()
    response = client.get("/api/v1/process")
    assert response.status_code == 200
    assert response.json() == []


def test_list_process_jobs_returns_all_created_jobs():
    _override_all_services()
    project_id, dataset_id = _create_project_and_dataset()

    created_ids = set()
    for features in (["parcels"], ["buildings"], ["roads"]):
        response = client.post(
            "/api/v1/process",
            json={"project_id": project_id, "dataset_id": dataset_id, "features": features},
        )
        created_ids.add(response.json()["job_id"])

    list_response = client.get("/api/v1/process")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body) == 3
    returned_ids = {job["job_id"] for job in body}
    assert returned_ids == created_ids
    # Each entry in the list should have the same shape as GET /process/{job_id}.
    for job in body:
        assert job["status"] == "completed"
        assert job["result"] is not None


def test_malformed_ai_output_marks_job_failed_with_safe_error():
    """Phase 7: an adapter that returns successfully but with output
    that fails schema validation must be treated as a pipeline failure,
    not marked "completed" and not an unhandled 500."""
    _override_all_services(ai_adapter=MalformedAIAdapter())
    project_id, dataset_id = _create_project_and_dataset()

    response = client.post(
        "/api/v1/process",
        json={"project_id": project_id, "dataset_id": dataset_id, "features": ["parcels"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"

    status_response = client.get(f"/api/v1/process/{body['job_id']}")
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["status"] == "failed"
    assert status_body["result"] is None
    assert status_body["error"] == "AI adapter output did not match the expected schema."
    # Safe error only - no leaked Pydantic internals, exception type, or traceback.
    assert "ValidationError" not in status_body["error"]
    assert "Traceback" not in status_body["error"]
    assert ".py" not in status_body["error"]


def test_malformed_gis_output_marks_job_failed_with_safe_error():
    _override_all_services(gis_adapter=MalformedGISAdapter())
    project_id, dataset_id = _create_project_and_dataset()

    response = client.post(
        "/api/v1/process",
        json={"project_id": project_id, "dataset_id": dataset_id, "features": ["parcels"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"

    status_response = client.get(f"/api/v1/process/{body['job_id']}")
    status_body = status_response.json()
    assert status_body["result"] is None
    assert status_body["error"] == "GIS adapter output did not match the expected schema."
    assert "ValidationError" not in status_body["error"]
    assert "Traceback" not in status_body["error"]


def test_malformed_analysis_output_marks_job_failed_with_safe_error():
    _override_all_services(analysis_adapter=MalformedAnalysisAdapter())
    project_id, dataset_id = _create_project_and_dataset()

    response = client.post(
        "/api/v1/process",
        json={"project_id": project_id, "dataset_id": dataset_id, "features": ["parcels"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"

    status_response = client.get(f"/api/v1/process/{body['job_id']}")
    status_body = status_response.json()
    assert status_body["result"] is None
    assert status_body["error"] == "Analysis adapter output did not match the expected schema."
    assert "ValidationError" not in status_body["error"]
    assert "Traceback" not in status_body["error"]
