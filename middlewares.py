from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request


class NoCacheHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        return response
