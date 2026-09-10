"""
VISTARA backend - application entrypoint.

This is the only place a FastAPI() instance is created. Routes,
middleware, and settings are all wired together here; business logic
belongs in app/services, not in this file.

Run locally (from the backend/ directory):
    uvicorn app.main:app --reload

Phase 6: configures stdlib logging once at import time, and registers
a global handler for unhandled exceptions. That handler only catches
the base `Exception` class - FastAPI/Starlette's exception middleware
resolves handlers by walking an exception's MRO and using the most
specific match it finds first, so `HTTPException` (used for every
existing 404/validation-style error across the app) and FastAPI's own
`RequestValidationError` (used for 422s) are matched by their own
more specific, already-registered handlers before ever reaching this
one. In other words: existing error responses are unaffected by
design, not by manually re-raising or excluding them here.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Safety net for any exception not already handled elsewhere (e.g. a
    genuine bug, not one of the domain errors every service already
    catches and translates to a specific HTTPException). Logs the real
    exception server-side and returns a safe, generic 500 response -
    never a stack trace or internal detail to the client.
    """
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal error occurred."},
    )
