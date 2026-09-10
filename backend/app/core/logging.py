"""
Lightweight structured logging configuration (Phase 6).

Uses only Python's standard library `logging` module - no new
dependency added to requirements.txt.

Every module under `app/` calls `logging.getLogger(__name__)` in the
usual Python way, which means each logger name is automatically
namespaced under "app" (e.g. "app.services.process_service"), since
that's the package's own dotted path. Those loggers have no handlers
of their own and propagate upward by default, so configuring a single
handler on the "app" logger here is enough to capture log output from
every module without touching them individually.

configure_logging() is idempotent - safe to call more than once (e.g.
once from app/main.py at import time, and again if a test imports it
directly) without adding duplicate handlers.
"""

import logging
import sys

_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)
    app_logger.addHandler(handler)

    _CONFIGURED = True
