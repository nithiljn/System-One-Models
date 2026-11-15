"""
Application Configuration Module.
Loads environment variables safely and defines centralized project settings.
Uses LRU caching to avoid redundant disk reads.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Central settings class holding all application constants and secrets."""

    def __init__(self) -> None:
        """Initialize settings and validate critical environment secrets."""
        self.GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        self.DECISION_MODEL: str = "gemini-decision-1"
        self.AUDIT_MODEL: str = "gemini-3.5-flash-lite"

        # Server networking settings (7860 matches Hugging Face Spaces default port)
        self.SERVER_HOST: str = "0.0.0.0"
        self.SERVER_PORT: int = 7860
        self.validate()

    def validate(self) -> None:
        """
        Validates that critical secrets exist.
        Raises ValueError if the GEMINI_API_KEY is missing.
        """
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "CRITICAL ERROR: GEMINI_API_KEY not found in environment. "
                "Please check your .env file."
            )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of Settings using LRU Cache.
    Reads from disk once and serves subsequent calls directly from RAM.
    """
    return Settings()
