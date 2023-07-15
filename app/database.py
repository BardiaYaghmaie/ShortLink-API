from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup - local
engine = create_engine("postgresql://postgres:1qaz2wsx@localhost/shortlinks_DBcontext")
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
