"""
Health check route.

Simple liveness endpoint the frontend (or CI, or a load balancer in a
future phase) can hit to confirm the backend is up and responding.
Deliberately has no dependencies on the database, AI, GIS, or
GIS-analysis services - those get their own readiness checks later.
"""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="VISTARA backend")
