from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), geolocation=(), payment=()"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory baseline limiter; Redis-backed limits replace it in multi-worker production."""
    def __init__(self, app, limit: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.limit, self.window_seconds = limit, window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/health", "/ready"}:
            return await call_next(request)
        now = monotonic()
        client = request.client.host if request.client else "unknown"
        window = self.requests[client]
        while window and window[0] <= now - self.window_seconds:
            window.popleft()
        if len(window) >= self.limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429, headers={"Retry-After": str(self.window_seconds)})
        window.append(now)
        return await call_next(request)
