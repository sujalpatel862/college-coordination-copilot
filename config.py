"""Centralized configuration for College Coordination Copilot.

All model and environment configuration lives here so the rest of the
application never hardcodes the model name or API key.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.is_file():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

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


def get_api_key() -> str:
    """Return the current GEMINI_API_KEY from environment."""
    return os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()


def validate_api_key(exit_on_failure: bool = False) -> bool:
    """Check if the API key is configured.

    If exit_on_failure is True, exits with a clear message (for CLI scripts).
    Otherwise returns False.
    """
    key = get_api_key()
    if not key:
        if exit_on_failure:
            sys.exit(
                "ERROR: GEMINI_API_KEY is not set. "
                "Copy .env.example to .env and add your key, "
                "or export GEMINI_API_KEY in your shell."
            )
        return False
    return True
