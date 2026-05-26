"""
GovernAI Studio — Gemini API Key Rotator
=========================================
Round-robin rotation across multiple Gemini API keys.
When one key hits 429, automatically rotates to the next.

Usage:
  Set GEMINI_API_KEYS in .env as comma-separated:
    GEMINI_API_KEYS=key1,key2,key3,...,key10

  Falls back to single GEMINI_API_KEY if GEMINI_API_KEYS is not set.
"""
import os
import threading
import time
from typing import Optional

import structlog

logger = structlog.get_logger()


class GeminiKeyRotator:
    """
    Thread-safe round-robin API key rotation for Gemini.
    
    Automatically skips keys that have been rate-limited,
    with a cooldown period before retrying exhausted keys.
    """

    COOLDOWN_SECONDS = 65  # Gemini rate limit window is ~60s

    def __init__(self):
        self._lock = threading.Lock()
        self._keys: list[str] = []
        self._current_index: int = 0
        self._cooldowns: dict[int, float] = {}  # index → cooldown_until timestamp
        self._load_keys()

    def _load_keys(self):
        """Load keys from GEMINI_API_KEYS (comma-separated) or GEMINI_API_KEY."""
        multi_keys = os.environ.get("GEMINI_API_KEYS", "")
        if multi_keys:
            self._keys = [k.strip() for k in multi_keys.split(",") if k.strip()]
        
        # Fallback to single key
        if not self._keys:
            single = os.environ.get("GEMINI_API_KEY", "")
            if single:
                self._keys = [single]

        logger.info("gemini_keys_loaded", count=len(self._keys))

    @property
    def key_count(self) -> int:
        return len(self._keys)

    def get_key(self) -> Optional[str]:
        """Get the next available API key (round-robin, skipping cooled-down keys)."""
        if not self._keys:
            return None

        with self._lock:
            now = time.time()
            # Try all keys starting from current index
            for _ in range(len(self._keys)):
                idx = self._current_index % len(self._keys)
                cooldown_until = self._cooldowns.get(idx, 0)

                if now >= cooldown_until:
                    # This key is available
                    self._current_index = (idx + 1) % len(self._keys)
                    return self._keys[idx]
                
                # Skip — this key is cooling down
                self._current_index = (idx + 1) % len(self._keys)

            # All keys are on cooldown — return the one with shortest remaining wait
            soonest_idx = min(self._cooldowns, key=self._cooldowns.get)
            wait = self._cooldowns[soonest_idx] - now
            logger.warning("all_keys_exhausted", wait_seconds=round(wait, 1))
            return self._keys[soonest_idx]

    def mark_exhausted(self, key: str):
        """Mark a key as rate-limited. It will be skipped for COOLDOWN_SECONDS."""
        with self._lock:
            try:
                idx = self._keys.index(key)
                self._cooldowns[idx] = time.time() + self.COOLDOWN_SECONDS
                available = sum(1 for i in range(len(self._keys))
                              if time.time() >= self._cooldowns.get(i, 0))
                logger.info("key_exhausted",
                           key_index=idx + 1,
                           total_keys=len(self._keys),
                           available_keys=available)
            except ValueError:
                pass

    def mark_success(self, key: str):
        """Clear cooldown for a key that succeeded (optional optimization)."""
        with self._lock:
            try:
                idx = self._keys.index(key)
                self._cooldowns.pop(idx, None)
            except ValueError:
                pass

    def get_stats(self) -> dict:
        """Get rotator status."""
        now = time.time()
        with self._lock:
            available = sum(1 for i in range(len(self._keys))
                          if now >= self._cooldowns.get(i, 0))
            return {
                "total_keys": len(self._keys),
                "available_keys": available,
                "exhausted_keys": len(self._keys) - available,
            }


# Singleton instance
_rotator: Optional[GeminiKeyRotator] = None


def get_rotator() -> GeminiKeyRotator:
    """Get or create the singleton key rotator."""
    global _rotator
    if _rotator is None:
        _rotator = GeminiKeyRotator()
    return _rotator
