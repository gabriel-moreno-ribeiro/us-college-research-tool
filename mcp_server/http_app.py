"""
HTTP transport wrapper with BYOK middleware, rate limiting, and health check.
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Mount

from .key_context import set_keys, clear_keys
from .server import mcp

logger = logging.getLogger("mcp_server.http")


# --- Log filter: redact any API key values ---
class KeyRedactingFilter(logging.Filter):
    """Prevent API keys from leaking into log output."""
    _sensitive_patterns: list[str] = []

    @classmethod
    def register_sensitive(cls, value: str) -> None:
        if value and len(value) > 4:
            cls._sensitive_patterns.append(value)

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern in self._sensitive_patterns:
            if pattern in msg:
                record.msg = str(record.msg).replace(pattern, "[REDACTED]")
                if record.args:
                    record.args = tuple(
                        str(a).replace(pattern, "[REDACTED]") if isinstance(a, str) else a
                        for a in record.args
                    ) if isinstance(record.args, tuple) else record.args
        return True


# Install redacting filter on all loggers
_redact_filter = KeyRedactingFilter()
logging.getLogger().addFilter(_redact_filter)


# --- Rate limiter (simple in-memory, per-IP, 60 req/min) ---
class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> tuple[bool, int]:
        """Returns (allowed, retry_after_seconds)."""
        now = time.time()
        cutoff = now - self.window
        hits = self._hits[client_ip]
        # Prune old entries
        self._hits[client_ip] = [t for t in hits if t > cutoff]
        hits = self._hits[client_ip]
        if len(hits) >= self.max_requests:
            retry_after = int(hits[0] - cutoff) + 1
            return False, retry_after
        hits.append(now)
        return True, 0


_rate_limiter = RateLimiter()


# --- BYOK Middleware ---
class BYOKMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract keys from headers
        scorecard_key = request.headers.get("x-college-scorecard-key")
        ss_key = request.headers.get("x-semantic-scholar-key")

        # Register for redaction (even if they're invalid)
        if scorecard_key:
            KeyRedactingFilter.register_sensitive(scorecard_key)
        if ss_key:
            KeyRedactingFilter.register_sensitive(ss_key)

        # Set in context
        set_keys(scorecard=scorecard_key, semantic_scholar=ss_key)
        try:
            response = await call_next(request)
        finally:
            clear_keys()
        return response


# --- Rate limit middleware ---
class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        allowed, retry_after = _rate_limiter.is_allowed(client_ip)
        if not allowed:
            return JSONResponse(
                {"error": "rate_limited", "message": "Too many requests", "retry_after": retry_after},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)


# --- Health check ---
async def health_check(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


def create_app() -> Starlette:
    """Create the full ASGI app with MCP + middleware."""
    # Get the MCP Starlette app (stateless for scalability on free tier)
    mcp_app = mcp.streamable_http_app(stateless_http=True)

    app = Starlette(
        routes=[
            Route("/health", health_check, methods=["GET"]),
            Mount("/", app=mcp_app),
        ],
        middleware=[
            Middleware(RateLimitMiddleware),
            Middleware(BYOKMiddleware),
        ],
    )
    return app
