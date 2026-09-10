"""
Phase 6: a lightweight test confirming logging is configured, without
asserting on exact log message content (which would be brittle and
would break on any harmless wording change to a log statement).
"""

import logging

from app.core.logging import configure_logging


def test_app_logger_is_configured():
    configure_logging()

    app_logger = logging.getLogger("app")

    assert app_logger.handlers, "expected at least one handler configured on the 'app' logger"
    assert app_logger.level == logging.INFO


def test_configure_logging_is_idempotent():
    """Calling it more than once must not add duplicate handlers."""
    configure_logging()
    configure_logging()
    configure_logging()

    app_logger = logging.getLogger("app")
    assert len(app_logger.handlers) == 1


def test_child_logger_propagates_to_app_logger():
    """
    Modules use logging.getLogger(__name__), e.g. "app.services.process_service" -
    confirm such a child logger has no handler of its own and relies on
    propagation up to the configured "app" logger, as documented.
    """
    configure_logging()

    child_logger = logging.getLogger("app.services.process_service")
    assert child_logger.handlers == []
    assert child_logger.propagate is True
