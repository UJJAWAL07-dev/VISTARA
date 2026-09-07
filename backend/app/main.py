"""
VISTARA backend - application entrypoint.

This is the only place a FastAPI() instance is created. Routes,
middleware, and settings are all wired together here; business logic
belongs in app/services, not in this file.

Run locally (from the backend/ directory):
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API connecting the VISTARA frontend with the AI, GIS, "
    "GIS-analysis, and database systems.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)
