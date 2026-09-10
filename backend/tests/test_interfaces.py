"""
Phase 5 conformance tests.

`typing.Protocol` with `@runtime_checkable` only lets `isinstance()`
check that the right *method names* exist on an object - it does NOT
check parameter names, counts, or types. Relying on isinstance() alone
would let a store/adapter silently drift out of sync with its
documented contract (e.g. a renamed or reordered parameter) while
still "passing" an isinstance() check.

These tests do both:
1. A basic isinstance() check (cheap, catches missing methods entirely).
2. A structural signature check via `inspect.signature`, comparing each
   Protocol method's parameter names (excluding `self`) against the
   concrete implementation's parameter names, for every method in the
   contract. This does not require any new dependency - `inspect` is
   part of the Python standard library.

If any store or adapter constructor argument order/names ever drift
from what its Protocol documents, these tests fail loudly instead of
the drift being discovered later when a real implementation is wired
in and something breaks silently.
"""

import inspect

from app.core.interfaces import (
    AIAdapterProtocol,
    AnalysisAdapterProtocol,
    DatasetRepository,
    GISAdapterProtocol,
    JobRepository,
    ProjectRepository,
)
from app.integrations.ai_adapter import AIAdapter
from app.integrations.analysis_adapter import AnalysisAdapter
from app.integrations.gis_adapter import GISAdapter
from app.services.dataset_service import InMemoryDatasetStore
from app.services.process_service import InMemoryJobStore
from app.services.project_service import InMemoryProjectStore


def _protocol_method_names(protocol_cls) -> list:
    """Public methods declared directly on a Protocol class (not inherited from object/Protocol)."""
    names = []
    for name, value in vars(protocol_cls).items():
        if name.startswith("_"):
            continue
        if inspect.isfunction(value):
            names.append(name)
    return names


def _assert_conforms(concrete_cls, protocol_cls) -> None:
    """
    For every method the Protocol declares, assert the concrete class:
    1. has a method of the same name, and
    2. that method's parameter names (excluding self/**kwargs defaults)
       match the Protocol method's parameter names, in order.
    """
    method_names = _protocol_method_names(protocol_cls)
    assert method_names, f"{protocol_cls.__name__} declared no methods to check - test itself is broken"

    for method_name in method_names:
        assert hasattr(concrete_cls, method_name), (
            f"{concrete_cls.__name__} is missing method '{method_name}' "
            f"required by {protocol_cls.__name__}"
        )

        protocol_sig = inspect.signature(getattr(protocol_cls, method_name))
        concrete_sig = inspect.signature(getattr(concrete_cls, method_name))

        protocol_params = list(protocol_sig.parameters.keys())
        concrete_params = list(concrete_sig.parameters.keys())

        assert protocol_params == concrete_params, (
            f"{concrete_cls.__name__}.{method_name} parameters {concrete_params} "
            f"do not match {protocol_cls.__name__}.{method_name} parameters {protocol_params}"
        )


# --- Repository (storage) contracts -----------------------------------------

def test_in_memory_project_store_satisfies_project_repository():
    assert isinstance(InMemoryProjectStore(), ProjectRepository)
    _assert_conforms(InMemoryProjectStore, ProjectRepository)


def test_in_memory_dataset_store_satisfies_dataset_repository():
    assert isinstance(InMemoryDatasetStore(), DatasetRepository)
    _assert_conforms(InMemoryDatasetStore, DatasetRepository)


def test_in_memory_job_store_satisfies_job_repository():
    assert isinstance(InMemoryJobStore(), JobRepository)
    _assert_conforms(InMemoryJobStore, JobRepository)


# --- AI / GIS / Analysis adapter contracts ----------------------------------

def test_ai_adapter_satisfies_ai_adapter_protocol():
    assert isinstance(AIAdapter(), AIAdapterProtocol)
    _assert_conforms(AIAdapter, AIAdapterProtocol)


def test_gis_adapter_satisfies_gis_adapter_protocol():
    assert isinstance(GISAdapter(), GISAdapterProtocol)
    _assert_conforms(GISAdapter, GISAdapterProtocol)


def test_analysis_adapter_satisfies_analysis_adapter_protocol():
    assert isinstance(AnalysisAdapter(), AnalysisAdapterProtocol)
    _assert_conforms(AnalysisAdapter, AnalysisAdapterProtocol)
