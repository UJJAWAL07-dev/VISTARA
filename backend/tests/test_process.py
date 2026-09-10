from typing import Any, Dict, List, Optional

from fastapi.testclient import TestClient

from app.integrations.ai_adapter import AIAdapter, AIAdapterError
from app.integrations.analysis_adapter import AnalysisAdapter
from app.integrations.gis_adapter import GISAdapter
from app.main import app
from app.models.job import Job
from app.services.process_service import InMemoryJobStore, ProcessingService, get_processing_service

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


def _override_service(store: Optional[InMemoryJobStore] = None) -> ProcessingService:
    """Give each test an isolated job store so tests don't leak state into each other."""
    service = ProcessingService(store=store or InMemoryJobStore())
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
    # Phase 4: orchestration is synchronous, so by the time POST returns,
    # the (mocked) pipeline has already finished successfully.
    assert body["status"] == "completed"
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
    # Phase 4: same reasoning as test_create_process_job_success - the mocked
    # pipeline has already completed by the time this job exists at all.
    assert body["status"] == "completed"


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


def test_pipeline_progresses_through_processing_before_completed():
    """Phase 4: confirms the job actually passes through 'processing',
    not just that it ends at 'completed' - using a store that records
    every status transition it observes."""
    store = RecordingJobStore()
    _override_service(store=store)

    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": ["parcels"]},
    )
    assert response.status_code == 201

    assert "processing" in store.status_history
    assert store.status_history.index("processing") < store.status_history.index("completed")


def test_completed_job_contains_ai_gis_and_analysis_result():
    _override_service()
    create_response = client.post(
        "/api/v1/process",
        json={
            "project_id": "project-001",
            "dataset_id": "dataset-001",
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
    service = ProcessingService(store=InMemoryJobStore(), ai_adapter=FailingAIAdapter())
    app.dependency_overrides[get_processing_service] = lambda: service

    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": ["parcels"]},
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
    _override_service()
    response = client.get("/api/v1/process")
    assert response.status_code == 200
    assert response.json() == []


def test_list_process_jobs_returns_all_created_jobs():
    _override_service()
    created_ids = set()
    for features in (["parcels"], ["buildings"], ["roads"]):
        response = client.post(
            "/api/v1/process",
            json={"project_id": "project-001", "dataset_id": "dataset-001", "features": features},
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
    service = ProcessingService(store=InMemoryJobStore(), ai_adapter=MalformedAIAdapter())
    app.dependency_overrides[get_processing_service] = lambda: service

    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": ["parcels"]},
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
    service = ProcessingService(store=InMemoryJobStore(), gis_adapter=MalformedGISAdapter())
    app.dependency_overrides[get_processing_service] = lambda: service

    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": ["parcels"]},
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
    service = ProcessingService(store=InMemoryJobStore(), analysis_adapter=MalformedAnalysisAdapter())
    app.dependency_overrides[get_processing_service] = lambda: service

    response = client.post(
        "/api/v1/process",
        json={"project_id": "project-001", "dataset_id": "dataset-001", "features": ["parcels"]},
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
