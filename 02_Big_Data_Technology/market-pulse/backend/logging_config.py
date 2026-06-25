"""
Centralised logging configuration for the Market Pulse backend.

Initialises the stdlib `logging` module with a consistent format and level.
Import this module early in the application entry point (i.e. before any
other local imports that may log) so that every logger across the project
inherits the same handlers and format.

Usage:
    import logging_config  # noqa: F401 — side-effect import

    # Then in any module:
    import logging
    logger = logging.getLogger(__name__)
    logger.info("cache warm-up complete")
"""

import logging

LOGGING_FORMAT = "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_FORMAT,
    datefmt=DATE_FORMAT,
)
