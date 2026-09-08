"""
Aggregates all /api/v1 routes into a single router.

New route modules (projects, datasets, processing, parcels, analysis,
export, auth) get included here as they're built in later phases.
Keeps main.py free of per-feature wiring.
"""

from fastapi import APIRouter

from app.routes import health, projects

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health.router)
api_v1_router.include_router(projects.router)
