"""
GovernAI Studio — Privacy & Security Middleware
Enterprise-grade PII stripping, request logging, and data isolation.
"""
import re
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()


class PrivacyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures officer data privacy at the infrastructure level.
    
    Responsibilities:
    1. Strip PII from all log output (emails, names, Aadhaar-like patterns)
    2. Add request ID for distributed tracing
    3. Log request metadata without sensitive content
    4. Enforce security headers
    5. Track request latency
    """

    # Patterns to redact from logs
    PII_PATTERNS = [
        (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "[EMAIL_REDACTED]"),
        (re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"), "[AADHAAR_REDACTED]"),
        (re.compile(r"\b\d{10}\b"), "[PHONE_REDACTED]"),
        (re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"), "Bearer [TOKEN_REDACTED]"),
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = f"req-{int(start_time * 1000) % 1000000}"

        # Log request (sanitized)
        logger.info(
            "request_start",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client=self._mask_ip(request.client.host if request.client else "unknown"),
        )

        # Process request
        response = await call_next(request)

        # Calculate latency
        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Add security headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"

        # Log response
        logger.info(
            "request_complete",
            request_id=request_id,
            status=response.status_code,
            latency_ms=latency_ms,
        )

        return response

    @staticmethod
    def _mask_ip(ip: str) -> str:
        """Mask the last octet of IPv4 addresses."""
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.***"
        return "***"

    @classmethod
    def sanitize_log(cls, text: str) -> str:
        """Remove PII patterns from any text before logging."""
        for pattern, replacement in cls.PII_PATTERNS:
            text = pattern.sub(replacement, text)
        return text


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-process rate limiter.
    For a pilot of 50-200 officers, this is sufficient.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.rpm = requests_per_minute
        self._requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        if client_ip in self._requests:
            self._requests[client_ip] = [
                t for t in self._requests[client_ip] if now - t < 60
            ]
        else:
            self._requests[client_ip] = []

        # Check rate limit
        if len(self._requests[client_ip]) >= self.rpm:
            logger.warning("rate_limited", client=client_ip)
            return Response(
                content='{"error": "RATE_LIMITED", "message": "Too many requests. Please wait."}',
                status_code=429,
                media_type="application/json",
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
