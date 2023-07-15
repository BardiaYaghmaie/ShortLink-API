from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import app

app_instance = FastAPI()

@app_instance.get("/{short_link}")
def redirect_to_url(short_link: str):
    return RedirectResponse(f"/api/urls/{short_link}")

app_instance.include_router(app, prefix="/api")
