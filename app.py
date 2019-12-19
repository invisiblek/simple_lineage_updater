import addrom
import delrom
import json
import os
import sqlite3
import sys

from datetime import datetime
from flask import Flask, jsonify, request, abort, render_template, send_from_directory
from flask_compress import Compress
from functools import wraps

app = Flask(__name__, static_url_path='')
Compress(app)
app.config.from_pyfile('app.cfg')
app.secret_key = app.config['SECRET_KEY']

db_filename = "updater.db"

constants = {}

if "SOURCE_URL" in app.config:
  constants['source_url'] = app.config['SOURCE_URL']
else:
  constants['source_url'] = "https://github.com/invisiblek/simple_lineage_updater"

if "PAGE_BANNER" in app.config:
  constants['page_banner'] = app.config['PAGE_BANNER']
else:
  constants['page_banner'] = "welcome to the updater server"

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
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  c.execute("SELECT * from rom where device = '{0}' and romtype = '{1}';".format(device, romtype))
  roms = c.fetchall()
  conn.commit()
  conn.close()
  zips = {}
  zips['response'] = []
  for r in roms:
    z = {}
    z['id'] = str(r[0])
    z['filename'] = r[1]
    z['datetime'] = r[2]
    z['device'] = r[3]
    z['version'] = r[4]
    z['romtype'] = r[5]
    z['md5sum'] = r[6]
    z['size'] = r[7]
    z['url'] = r[8]
    zips['response'].append(z)
  return jsonify(zips)

@app.route('/')
def root():
  devices = {}
  roms = {}

  conn = sqlite3.connect(db_filename)
  c = conn.cursor()

  c.execute("SELECT DISTINCT r.device, d.oem, d.name from rom r inner join device d on r.device = d.model order by r.device;")
  for row in c.fetchall():
    c.execute("SELECT r.url from rom r where device ='" + row[0] + "' order by r.datetime desc limit 1;")
    for l in c.fetchall():
      latest = l[0]
      break
    devices[row[0]] = { "device": row[0], "oem": row[1], "name": row[2], "latest": latest }

  c.execute("SELECT r.filename, r.datetime, r.romsize, r.url from rom r order by r.datetime desc limit 10;")
  for row in c.fetchall():
    roms[row[1]] = { "filename": row[0], "datetime": datetime.fromtimestamp(row[1]).strftime("%m/%d/%Y, %H:%M:%S"), "romsize": str(round(row[2]/(1024*1024),2)) + "MB", "url": row[3] }

  conn.commit()
  conn.close()

  return render_template('index.html', devices=devices, roms=roms, constants=constants)

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
    return "rom added!"
  except:
    return abort(400)

@app.route('/addrecovery', methods=['POST','GET'])
@api_key_required
def addnewrecovery():
  # we capture GET here so it overrides the dynamic route for devices below
  if request.method != 'POST':
    return abort(403)
  try:
    j = request.json
    addrecovery.add(j['filename'], j['device'], j['url'])
    return "recovery added!"
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
  d = {}
  roms = {}
  recovery = {}

  conn = sqlite3.connect(db_filename)
  c = conn.cursor()

  c.execute("SELECT d.model, d.oem, d.name from device d where d.model = '" + device + "';")
  for row in c.fetchall():
    d = { "device": row[0], "oem": row[1], "name": row[2] }
    break

  c.execute("SELECT r.filename, r.datetime, r.romsize, r.url from rom r where r.device = '" + device + "' order by r.filename desc;")
  for row in c.fetchall():
    roms[row[0]] = { "filename": row[0], "datetime": datetime.fromtimestamp(row[1]).strftime("%m/%d/%Y, %H:%M:%S"), "romsize": str(round(row[2]/(1024*1024),2)) + "MB", "url": row[3] }

  c.execute("SELECT r.url from recovery r where r.device = '" + device + "' order by r.id desc limit 1;")
  for row in c.fetchall():
    recovery = { "url": row[0] }
    break

  conn.commit()
  conn.close()

  return render_template('device.html', device=d, roms=roms, constants=constants, recovery=recovery)
