from model import *
from sqlalchemy import *

class Device(db.Model):
  __tablename__ = 'device'
  id = Column(Integer, primary_key=True)
  model = Column(String(255))
  oem = Column(String(255))
  name = Column(String(255))

class Rom(db.Model):
  __tablename__ = 'rom'
  id = Column(Integer, primary_key=True)
  filename = Column(String(255))
  datetime = Column(Integer)
  device = Column(String(255))
  version = Column(String(255))
  romtype = Column(String(255))
  md5sum = Column(String(255))
  romsize = Column(Integer)
  url = Column(String(255))

class Recovery(db.Model):
  __tablename__ = "recovery"
  id = Column(Integer, primary_key=True)
  filename = Column(String(255))
  device = Column(String(255))
  url = Column(String(255))
