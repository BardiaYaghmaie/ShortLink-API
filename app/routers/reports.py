from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import URL
from ..database import get_db
from pydantic import BaseModel

router = APIRouter()

class URLResponse(BaseModel):
    id: str
    url: str
    click_count: int
    is_enabled: bool

@router.get("/")
def get_all_urls(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    return [URLResponse(id=url.id, url=url.url, click_count=url.click_count, is_enabled=url.is_enabled) for url in urls]

@router.get("/{short_link}")
def get_url(short_link: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == short_link).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    return URLResponse(id=url.id, url=url.url, click_count=url.click_count, is_enabled=url.is_enabled)

@router.put("/{short_link}/toggle_enabled")
def toggle_link_enabled(short_link: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == short_link).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    url.is_enabled = not url.is_enabled
    db.commit()
    return {"message": "Link status toggled successfully", "is_enabled": url.is_enabled}

@router.delete("/{short_link}/delete")
def delete_link(short_link: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == short_link).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(url)
    db.commit()
    return {"message": "Link deleted successfully"}
