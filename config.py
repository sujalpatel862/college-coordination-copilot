"""Centralized configuration for College Coordination Copilot.

All model and environment configuration lives here so the rest of the
application never hardcodes the model name or API key.
"""

import os
import sys

# --- API key ---------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# --- Model configuration ---------------------------------------------------

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "").strip()
ENABLE_FALLBACK = os.getenv("ENABLE_MODEL_FALLBACK", "false").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)


def validate_api_key() -> None:
    """Exit early with a clear message if the API key is missing.

    Called at import time of ai_service so downstream code can assume the
    key exists.
    """
    if not GEMINI_API_KEY:
        sys.exit(
            "ERROR: GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and add your key, "
            "or export GEMINI_API_KEY in your shell."
        )
