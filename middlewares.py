from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware import Middleware


def add_no_cache_header_middleware(app: FastAPI):
    async def middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        return response

    app.middleware("http")(middleware)
