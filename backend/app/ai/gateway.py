"""
GovernAI Studio — Multi-Provider LLM Gateway
Routes requests across 4 free LLM providers with smart failover.
Total free capacity: ~95+ RPM, ~40K requests/day.
"""
import os
import time
import asyncio
from collections import defaultdict
from typing import Optional

import litellm
import structlog

from app.config import Settings
from app.ai.key_rotator import get_rotator

logger = structlog.get_logger()

# Suppress LiteLLM verbose logging
litellm.set_verbose = False


class ProviderBudget:
    """Tracks per-provider rate limit usage."""

    def __init__(self, rpm_limit: int, daily_limit: int):
        self.rpm_limit = rpm_limit
        self.daily_limit = daily_limit
        self.rpm_count = 0
        self.daily_count = 0
        self.rpm_window_start = time.time()
        self.daily_window_start = time.time()

    def has_budget(self) -> bool:
        now = time.time()
        # Reset RPM counter every 60 seconds
        if now - self.rpm_window_start >= 60:
            self.rpm_count = 0
            self.rpm_window_start = now
        # Reset daily counter every 24 hours
        if now - self.daily_window_start >= 86400:
            self.daily_count = 0
            self.daily_window_start = now

        return self.rpm_count < self.rpm_limit and self.daily_count < self.daily_limit

    def record_usage(self):
        self.rpm_count += 1
        self.daily_count += 1

    def get_stats(self) -> dict:
        return {
            "rpm_used": self.rpm_count,
            "rpm_limit": self.rpm_limit,
            "daily_used": self.daily_count,
            "daily_limit": self.daily_limit,
        }


# AI Role → Provider preference mapping
ROLE_PREFERENCES = {
    "director":        ["gemini", "groq", "cerebras", "sambanova"],
    "npc_dialogue":    ["groq", "cerebras", "sambanova", "gemini"],  # Speed first
    "whisperer":       ["gemini", "groq", "cerebras", "sambanova"],  # Reasoning first
    "drafting_partner": ["cerebras", "groq", "sambanova", "gemini"],
    "coach":           ["gemini", "groq", "cerebras", "sambanova"],
    "general":         ["gemini", "groq", "cerebras", "sambanova"],
}

# AI Role → Default generation parameters
ROLE_DEFAULTS = {
    "director":        {"temperature": 0.4, "max_tokens": 1500},
    "npc_dialogue":    {"temperature": 0.7, "max_tokens": 800},
    "whisperer":       {"temperature": 0.2, "max_tokens": 1000},
    "drafting_partner": {"temperature": 0.3, "max_tokens": 2000},
    "coach":           {"temperature": 0.5, "max_tokens": 4500},
    "general":         {"temperature": 0.5, "max_tokens": 2000},
}


class LLMGateway:
    """
    Multi-provider LLM gateway with:
    - Role-based routing (each AI role → optimal provider)
    - Automatic failover (if primary exhausted, try next)
    - Rate limit tracking per provider
    - Usage statistics
    """

    PROVIDERS = {
        "gemini": "gemini/gemini-2.5-flash",
        "groq": "groq/llama-3.3-70b-versatile",
        "cerebras": "cerebras/llama3.1-8b",
        "sambanova": "sambanova/Meta-Llama-3.3-70B-Instruct",
    }

    def __init__(self, settings: Settings):
        self.settings = settings
        self.budgets: dict[str, ProviderBudget] = {}
        self.gemini_rotator = get_rotator()

        # Initialize budgets and set API keys
        provider_configs = {
            "gemini":    (settings.GEMINI_API_KEY, settings.GEMINI_RPM, 1500),
            "groq":      (settings.GROQ_API_KEY, settings.GROQ_RPM, 14400),
            "cerebras":  (settings.CEREBRAS_API_KEY, settings.CEREBRAS_RPM, 14400),
            "sambanova": (settings.SAMBANOVA_API_KEY, settings.SAMBANOVA_RPM, 10000),
        }

        # Scale Gemini RPM by number of keys
        gemini_rpm = settings.GEMINI_RPM * max(self.gemini_rotator.key_count, 1)

        for name, (api_key, rpm, daily) in provider_configs.items():
            if api_key or (name == "gemini" and self.gemini_rotator.key_count > 0):
                effective_rpm = gemini_rpm if name == "gemini" else rpm
                effective_daily = 1500 * self.gemini_rotator.key_count if name == "gemini" else daily
                self.budgets[name] = ProviderBudget(rpm_limit=effective_rpm, daily_limit=effective_daily)
                # LiteLLM reads these from env
                env_key = f"{name.upper()}_API_KEY"
                os.environ[env_key] = api_key
                logger.info("provider_registered", provider=name, rpm=effective_rpm)
            else:
                logger.warning("provider_skipped_no_key", provider=name)

    def get_active_providers(self) -> list[str]:
        return list(self.budgets.keys())

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        role: str = "general",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """
        Generate a response with smart routing and auto-failover.

        Args:
            system_prompt: System instructions for the LLM
            user_prompt: The user/officer message
            role: AI role (director, npc_dialogue, whisperer, drafting_partner, coach)
            temperature: Override default temperature for this role
            max_tokens: Override default max_tokens for this role
            stream: Whether to stream the response

        Returns:
            Generated text string (or async generator if streaming)
        """
        # Get role defaults
        defaults = ROLE_DEFAULTS.get(role, ROLE_DEFAULTS["general"])
        temp = temperature if temperature is not None else defaults["temperature"]
        tokens = max_tokens if max_tokens is not None else defaults["max_tokens"]

        # Get provider preference order for this role
        preferred = ROLE_PREFERENCES.get(role, ROLE_PREFERENCES["general"])

        # Try each provider in preference order
        for provider_name in preferred:
            if provider_name not in self.budgets:
                continue

            budget = self.budgets[provider_name]
            if not budget.has_budget():
                logger.debug("provider_exhausted", provider=provider_name, role=role)
                continue

            model = self.PROVIDERS[provider_name]

            # For Gemini: rotate API key before each call
            if provider_name == "gemini":
                rotated_key = self.gemini_rotator.get_key()
                if rotated_key:
                    os.environ["GEMINI_API_KEY"] = rotated_key

            try:
                response = await litellm.acompletion(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temp,
                    max_tokens=tokens,
                    stream=stream,
                    timeout=30,
                    api_key=rotated_key if provider_name == "gemini" and rotated_key else None,
                )

                budget.record_usage()
                if provider_name == "gemini" and rotated_key:
                    self.gemini_rotator.mark_success(rotated_key)
                logger.info(
                    "llm_success",
                    provider=provider_name,
                    role=role,
                    rpm_used=budget.rpm_count,
                )

                if stream:
                    return response  # Return async generator
                return response.choices[0].message.content

            except Exception as e:
                error_str = str(e)
                # On 429, mark this Gemini key as exhausted and retry with next key
                if provider_name == "gemini" and "429" in error_str and rotated_key:
                    self.gemini_rotator.mark_exhausted(rotated_key)
                    next_key = self.gemini_rotator.get_key()
                    if next_key and next_key != rotated_key:
                        logger.info("gemini_key_rotated", role=role)
                        os.environ["GEMINI_API_KEY"] = next_key
                        try:
                            response = await litellm.acompletion(
                                model=model,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt},
                                ],
                                temperature=temp,
                                max_tokens=tokens,
                                stream=stream,
                                timeout=30,
                                api_key=next_key,
                            )
                            budget.record_usage()
                            self.gemini_rotator.mark_success(next_key)
                            if stream:
                                return response
                            return response.choices[0].message.content
                        except Exception:
                            self.gemini_rotator.mark_exhausted(next_key)

                logger.warning(
                    "provider_failed",
                    provider=provider_name,
                    role=role,
                    error=error_str[:100],
                )
                continue

        # All providers exhausted
        logger.error("all_providers_exhausted", role=role)
        raise LLMBusyError(
            "All LLM providers are at capacity. Please wait a moment and try again."
        )

    def get_usage_stats(self) -> dict:
        """Return current usage stats for all providers."""
        return {name: budget.get_stats() for name, budget in self.budgets.items()}


class LLMBusyError(Exception):
    """Raised when all LLM providers are at rate limit."""
    pass
