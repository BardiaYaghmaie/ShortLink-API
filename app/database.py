from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Database setup - local
engine = create_engine("postgresql://postgres:1qaz2wsx@shortlink-api-db-1/shortlinks_DBcontext")
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

