from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Database setup - local
engine = create_engine("postgresql://postgres:1qaz2wsx@localhost/shortlinks_DBcontext")
#engine = create_engine("postgresql://postgres:1qaz2wsx@shortlink-db/shortlinks_DBcontext")
SessionLocal = sessionmaker(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
