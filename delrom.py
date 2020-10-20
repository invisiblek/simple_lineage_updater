#!/usr/bin/env python3
#

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

def delete(filename):
  Rom.query.filter(Rom.filename==filename).delete()
  db.session.commit()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--filename", required=True)
  args = parser.parse_args()

  delete(args.filename)
