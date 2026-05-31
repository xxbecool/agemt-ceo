"""
Tenant middleware: extracts tenant_id from JWT and stores in request state.
This enables downstream handlers to access the current tenant without re-parsing tokens.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.security import verify_token


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Extracts tenant context from the Bearer token and stores it on request.state.
    Routes that don't require auth (e.g., /health, /docs) are skipped gracefully.
    """

    SKIP_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        # Initialise with None so downstream can check
        request.state.tenant_id = None
        request.state.user_id = None
        request.state.user_role = None

        if request.url.path not in self.SKIP_PATHS:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ").strip()
                try:
                    payload = verify_token(token, token_type="access")
                    request.state.tenant_id = payload.get("tenant_id")
                    request.state.user_id = payload.get("sub")
                    request.state.user_role = payload.get("role")
                except Exception:
                    pass  # Let the auth dependency handle the 401

        return await call_next(request)
