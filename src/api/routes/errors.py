"""Sanitized HTTP errors for local model failures."""

import logging

from fastapi import HTTPException

logger = logging.getLogger(__name__)


def model_error(exc: Exception) -> HTTPException:
    # Do not log prompts, response bodies, URLs, or exception messages.
    logger.warning("Local LLM request failed (%s)", type(exc).__name__)
    return HTTPException(
        status_code=502, detail="Local LLM failed to return a valid response"
    )
