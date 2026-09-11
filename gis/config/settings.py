"""
Path and environment configuration for the GIS engine.

No machine-specific or absolute paths are hardcoded here (section 30).
Everything resolves relative to the repo root, and every path can be
overridden with an environment variable so the project works
identically after `git clone` on any team member's machine.
"""

import os
from pathlib import Path


def _resolve_project_root() -> Path:
    """
    gis/config/settings.py -> gis/config -> gis -> <repo root>
    """
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT: Path = _resolve_project_root()
GIS_ROOT: Path = PROJECT_ROOT / "gis"

# Where sample datasets live (owned by Member 6 — we only READ from here).
DATASET_ROOT: Path = Path(
    os.environ.get("VISTARA_DATASET_ROOT", PROJECT_ROOT / "datasets" / "sample")
)

# Where the GIS engine writes its own processed/exported output.
# Kept inside /gis so we never write into another member's folder.
OUTPUT_ROOT: Path = Path(
    os.environ.get("VISTARA_GIS_OUTPUT_ROOT", GIS_ROOT / "_output")
)

# Expected sample dataset layout (matches section 11).
# These are READ locations, not owned/created by the GIS engine.
PARCELS_DIR: Path = DATASET_ROOT / "parcels"
BUILDINGS_DIR: Path = DATASET_ROOT / "buildings"
ROADS_DIR: Path = DATASET_ROOT / "roads"
LANDUSE_DIR: Path = DATASET_ROOT / "land-use"
IMAGERY_DIR: Path = DATASET_ROOT / "imagery"
DSM_DIR: Path = DATASET_ROOT / "dsm"
DTM_DIR: Path = DATASET_ROOT / "dtm"


def ensure_dir(path: Path) -> Path:
    """
    Create a directory (and parents) if it doesn't exist yet.
    Used only for OUTPUT_ROOT-style paths that the GIS engine owns —
    never call this on dataset/database/other-member directories.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
