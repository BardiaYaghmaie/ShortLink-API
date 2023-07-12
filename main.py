from typing import Callable, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes , OpenIdConnect 
import string, random, os, re, requests
from jose import jwt
from pydantic import BaseModel

app = FastAPI()

# Database setup - local
engine = create_engine("postgresql://postgres:1qaz2wsx@localhost/shortlinks_DBcontext")
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)
Base = declarative_base()

class URL(Base):
    __tablename__ = "urls"
    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    click_count = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)  # Added is_enabled attribute

class ShortenLinkRequest(BaseModel):
    long_link: str
    is_enabled: bool = True
    short_link: Optional[str] = None

class URLResponse(BaseModel):
    id: str
    url: str
    click_count: int
    is_enabled: bool  # Added is_enabled attribute

# Create database
Base.metadata.create_all(bind=engine)

def generate_short_link():
    characters = string.ascii_letters + string.digits
    short_link = ''.join(random.choice(characters) for _ in range(7))
    return short_link

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorten_link")
def shorten_link(
    request: ShortenLinkRequest,
    db: Session = Depends(get_db),
    # token_data: dict = Depends(get_token_data)
):
    valid_url = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

    if request.short_link:
        short_link = request.short_link
    else:
        short_link = generate_short_link()
    if re.match(valid_url, request.long_link):
        link = URL(id=short_link, url=request.long_link, is_enabled=request.is_enabled)
        db.add(link)
        db.commit()
        return {"short_link": f"accl.ir/{short_link}"}
    else:
        raise HTTPException(status_code=400, detail="link not valid. try adding http[s]://")

@app.get("/{short_link}")
def redirect(short_link: str, db: Session = Depends(get_db)):
    link = db.query(URL).filter(URL.id == short_link).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if not link.is_enabled:
        raise HTTPException(status_code=403, detail="Link is disabled")
    link.click_count += 1
    db.commit()
    return RedirectResponse(link.url, status_code=301)

@app.get("/urls/report")
def get_all_urls(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    return [URLResponse(id=url.id, url=url.url, click_count=url.click_count, is_enabled=url.is_enabled) for url in urls]

@app.get("/urls/{short_link}/report")
def get_url(short_link: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == short_link).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    return URLResponse(id=url.id, url=url.url, click_count=url.click_count, is_enabled=url.is_enabled)

@app.put("/urls/{short_link}/toggle_enabled")
def toggle_link_enabled(short_link: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == short_link).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    url.is_enabled = not url.is_enabled  # Toggle the value of is_enabled attribute
    db.commit()
    return {"message": "Link status toggled successfully", "is_enabled": url.is_enabled}

@app.delete("/urls/{short_link}/delete")
def delete_link(short_link: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.id == short_link).first()
    if not url:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(url)
    db.commit()
    return {"message": "Link deleted successfully"}



