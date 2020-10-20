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

parser = argparse.ArgumentParser()
parser.add_argument("--filename", required=True)
parser.add_argument("--device", required=True)
parser.add_argument("--url", required=True)
args = parser.parse_args()

Recovery.query.filter(Recovery.filename==args.filename).delete()
db.session.commit()

r = Recovery(filename=args.filename,
             device=args.device,
             url=args.url)

db.session.add(r)
db.session.commit()
