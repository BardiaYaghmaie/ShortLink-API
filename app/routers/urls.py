from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import URL
from ..database import get_db
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import string
import random
import re

router = APIRouter()


class ShortenLinkRequest(BaseModel):
    long_link: str
    is_enabled: bool = True
    short_link: Optional[str] = None


def generate_short_link():
    characters = string.ascii_letters + string.digits
    short_link = ''.join(random.choice(characters) for _ in range(7))
    return short_link


@router.post("/shorten_link")
def shorten_link(
        request: ShortenLinkRequest,
        db: Session = Depends(get_db),
):
    valid_url = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9(" \
                ")@:%_\\+.~#?&\\/=]*)$"

    if request.short_link:
        repeat_check = db.query(URL).filter(URL.id == request.short_link).first()
        if repeat_check:
            raise HTTPException(status_code=400, detail="Shortlink is already in use")
        else:
            short_link = request.short_link
    else:
        short_link = generate_short_link()

    if re.match(valid_url, request.long_link):
        link = URL(id=short_link, url=request.long_link, is_enabled=request.is_enabled)
        db.add(link)
        db.commit()
        return {"short_link": f"your-domain.xyz/{short_link}"}
    else:
        raise HTTPException(status_code=400, detail="link not valid. try adding http[s]://")


@router.get("/{short_link}")
async def redirect(short_link: str, db: Session = Depends(get_db)):
    link = db.query(URL).filter(URL.id == short_link).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if not link.is_enabled:
        raise HTTPException(status_code=403, detail="Link is disabled")
    link.click_count += 1
    db.commit()
    return RedirectResponse(link.url, status_code=301)


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
