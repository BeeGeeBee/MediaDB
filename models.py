from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


__author__ = 'Bernard'

Base = declarative_base()


class Media(Base):
    __tablename__ = 'media'
    mediaid = Column(Integer, primary_key=True)
    mediatype = Column(String(10))
    description = Column(String(250))
    url = Column(String(250))
    barcode = Column(String(20))
    timestamp = Column(DateTime)
