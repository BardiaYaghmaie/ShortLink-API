from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class URL(Base):
    __tablename__ = "urls"
    id = Column(String, primary_key=True, index=True)
    url = Column(String)
    click_count = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=True)

    click_data = relationship("ClickData", backref="url", cascade="all, delete")


class ClickData(Base):
    __tablename__ = "click_data"
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(String, ForeignKey("urls.id"))
    ip_address = Column(String)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
