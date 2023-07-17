from datetime import datetime
import pytz


from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware import Middleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.requests import Request
from app import app
from user_agents import parse

from app.database import get_db
from app.models import URL, ClickData
from middlewares import NoCacheHeaderMiddleware

app_instance = FastAPI(middleware=[Middleware(NoCacheHeaderMiddleware)])


@app_instance.get("/{short_link}")
async def redirect(
        request: Request, short_link: str, response: Response, db: Session = Depends(get_db),
):
    link = db.query(URL).filter(URL.id == short_link).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    if not link.is_enabled:
        raise HTTPException(status_code=403, detail="Link is disabled")
    link.click_count += 1

    # Capture click data
    ip_address = request.client.host
    user_agent = parse(request.headers.get("User-Agent"))
    tehran_timezone = pytz.timezone("Asia/Tehran")
    timestamp= datetime.now(tz=tehran_timezone)
    print(timestamp)
    browser = user_agent.browser.family
    os = user_agent.os.family + ' ' + user_agent.os.version_string
    click_data = ClickData(url_id=link.id, ip_address=ip_address, browser=browser, os=os, timestamp=timestamp)
    db.add(click_data)

    db.commit()
    response.headers["Cache-Control"] = "no-cache"
    return RedirectResponse(link.url, status_code=301)


app_instance.include_router(app, prefix="/api")
