#!/usr/bin/env python3
#

import delrom
import argparse
import os
import sqlite3
import sys

from classes import *
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from model import *
from sqlalchemy import *

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.app_context().push()
config = current_app.config

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config['DB_NAME']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def add(filename, device, version, romtype, md5, romsize, url, dt):
  Rom.query.filter(Rom.filename==filename).delete()
  db.session.commit()

  r = Rom(filename=filename,
          device=device,
          version=version,
          romtype=romtype,
          md5sum=md5,
          romsize=romsize,
          url=url,
          datetime=dt)
  db.session.add(r)
  db.session.commit()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--filename", required=True)
  parser.add_argument("--device", required=True)
  parser.add_argument("--version", required=True)
  parser.add_argument("--romtype", required=True)
  parser.add_argument("--md5sum", required=True)
  parser.add_argument("--romsize", required=True)
  parser.add_argument("--url", required=True)
  parser.add_argument("--datetime", required=True)
  args = parser.parse_args()

  add(args.filename, args.device, args.version, args.romtype, args.md5sum, args.romsize, args.url, args.datetime)
