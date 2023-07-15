from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class URL(Base):
    __tablename__ = "urls"
    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    click_count = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)
