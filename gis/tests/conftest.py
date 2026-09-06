"""Shared pytest fixtures for the GIS engine test suite."""

import shutil

import pytest

from gis.config import OUTPUT_ROOT
from gis.loaders.synthetic_fixtures import (
    make_synthetic_parcels,
    make_synthetic_raster,
)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_output():
    """Keep synthetic tests isolated from real datasets and clean afterward."""
    test_dir = OUTPUT_ROOT / "synthetic"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    yield
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def synthetic_parcels_path():
    return make_synthetic_parcels()


@pytest.fixture
def synthetic_raster_path():
    return make_synthetic_raster()
