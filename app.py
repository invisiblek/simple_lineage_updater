import addrom
import delrom
import json
import os
import sqlite3
import sys

from classes import *
from datetime import datetime
from flask import Flask, jsonify, request, abort, render_template, send_from_directory
from flask_compress import Compress
from functools import wraps
from model import *

app = Flask(__name__, static_url_path='')
Compress(app)
app.config.from_pyfile('app.cfg')
app.secret_key = app.config['SECRET_KEY']

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config['DB_NAME']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

constants = {}

if "SOURCE_URL" in app.config:
  constants['source_url'] = app.config['SOURCE_URL']
else:
  constants['source_url'] = "https://github.com/invisiblek/simple_lineage_updater"

if "PAGE_BANNER" in app.config:
  constants['page_banner'] = app.config['PAGE_BANNER']
else:
  constants['page_banner'] = "welcome to the updater server"

@app.template_filter('datetimefromtimestamp')
def datetimefromtimestamp(value):
  return datetime.fromtimestamp(value).strftime("%m/%d/%Y, %H:%M:%S")

# Any function decorated with this must include a header that specifies "Apikey: <key>"
# which matches the app.cfg value for API_KEY
def api_key_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if 'Apikey' in request.headers and "API_KEY" in app.config:
      if app.config['API_KEY'] == request.headers.get('Apikey'):
        return f(*args, **kwargs)
    return abort(403)
  return decorated_function

@app.route('/static/<path:path>')
def send_static(path):
  return send_from_directory('static', path)

@app.route('/api/v1/<string:device>/<string:romtype>/<string:incrementalversion>')
def index(device, romtype, incrementalversion):
  roms = Rom.query.filter_by(device=device, romtype=romtype)
  zips = {}
  zips['response'] = []
  for r in roms:
    z = {}
    z['id'] = str(r.id)
    z['filename'] = r.filename
    z['datetime'] = r.datetime
    z['device'] = r.device
    z['version'] = r.version
    z['romtype'] = r.romtype
    z['md5sum'] = r.md5sum
    z['size'] = r.romsize
    z['url'] = r.url
    zips['response'].append(z)
  return jsonify(zips)

@app.route('/')
def root():
  latest = {}
  devices = Device.query.join(Rom, Device.model == Rom.device).order_by(Device.model)
  for d in devices:
    latest[d.model] = Rom.query.filter_by(device=d.model).order_by(desc(Rom.datetime)).first().url
  roms = Rom.query.order_by(desc(Rom.datetime)).limit(10)

  return render_template('index.html', devices=devices, roms=roms, constants=constants, latest=latest)

# Json example:
# {
#   "device": "bonito",
#   "filename": "test.zip",
#   "version": "17.0",
#   "romtype": "unofficial",
#   "md5": "1234567",
#   "url": "http://www.google.com",
#   "datetime": "1574582999",
#   "romsize": "12345"
# }
@app.route('/addrom', methods=['POST','GET'])
@api_key_required
def addnewrom():
  # we capture GET here so it overrides the dynamic route for devices below
  if request.method != 'POST':
    return abort(403)
  try:
    j = request.json
    addrom.add(j['filename'], j['device'], j['version'], j['romtype'], j['md5'], j['romsize'], j['url'], j['datetime'])
    return "added!"
  except:
    return abort(400)

# Json example:
# {
#   "filename": "test.zip"
# }
@app.route('/delrom', methods=['POST','GET'])
@api_key_required
def deleterom():
  # we capture GET here so it overrides the dynamic route for devices below
  if request.method != 'POST':
    return abort(403)
  try:
    j = request.json
    delrom.delete(j['filename'])
    return "deleted!"
  except:
    return abort(400)

@app.route('/<string:device>')
def device(device):
  d = Device.query.filter_by(model=device).first()
  roms = Rom.query.filter_by(device=device).order_by(desc(Rom.datetime))
  recovery = Recovery.query.filter_by(device=device).order_by(desc(Recovery.id)).first()
  return render_template('device.html', device=d, roms=roms, constants=constants, recovery=recovery)
