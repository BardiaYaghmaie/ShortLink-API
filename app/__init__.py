import fastapi
from .routers.urls import router as urls_router
from .routers.reports import router as reports_router
from fastapi import APIRouter


app = APIRouter()

app.include_router(urls_router, prefix="/urls", tags=["URLs"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
