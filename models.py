from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


__author__ = 'Bernard'

Base = declarative_base()


class Media(Base):
    __tablename__ = 'media'
    mediaid = Column(Integer, primary_key=True)
    mediatype = Column(String(10))
    title = Column(String(250))
    description = Column(String(250))
    url = Column(String(250))
    barcode = Column(String(20))
    locationid = Column(Integer)
    timestamp = Column(DateTime)


class Locations(Base):
    __tablename__ = 'locations'
    locationid = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(250))
    sublocation = Column(String(50))


class BarcodesLoaded(Base):
    __tablename__ = 'barcodesloaded'
    barcode = Column(String(20), primary_key=True)
    status = Column(Integer)
    timestamp = Column(DateTime)
