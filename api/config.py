"""Application configuration from environment variables.

Centralises all config so there's one source of truth and no
scattered os.environ.get() calls across the codebase.
"""

import logging
import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
IS_STAGING = ENVIRONMENT == "staging"
IS_DEVELOPMENT = ENVIRONMENT == "development"

# Logging: verbose in dev/staging, quieter in prod
LOG_LEVEL = logging.DEBUG if not IS_PRODUCTION else logging.WARNING

# Model confidence threshold (below this → low-confidence warning)
MODEL_CONFIDENCE_THRESHOLD = float(os.environ.get("MODEL_CONFIDENCE_THRESHOLD", "0.3"))


def setup_logging() -> None:
    """Configure logging based on the current environment."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("api")
    logger.setLevel(LOG_LEVEL)
    logger.info("Environment: %s | Log level: %s", ENVIRONMENT, logging.getLevelName(LOG_LEVEL))
