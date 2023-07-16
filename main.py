from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from app import app
from app.database import get_db
from app.models import URL


class NoCacheHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        return response


app_instance = FastAPI(middleware=[Middleware(NoCacheHeaderMiddleware)])


@app_instance.get("/{short_link}")
async def redirect(short_link: str, response: Response, db: Session = Depends(get_db)):
    link = db.query(URL).filter(URL.id == short_link).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if not link.is_enabled:
        raise HTTPException(status_code=403, detail="Link is disabled")
    link.click_count += 1
    db.commit()
    response.headers["Cache-Control"] = "no-cache"
    return RedirectResponse(link.url, status_code=301)


app_instance.include_router(app, prefix="/api")
