import os
import sqlite3

from datetime import datetime
from flask import Flask, jsonify, request, abort, render_template, send_from_directory
from flask_compress import Compress

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
    roms[row[0]] = { "filename": row[0], "datetime": datetime.fromtimestamp(row[1]).strftime("%m/%d/%Y, %H:%M:%S"), "romsize": str(round(row[2]/(1024*1024),2)) + "MB", "url": row[3] }

  conn.commit()
  conn.close()

  return render_template('index.html', devices=devices, roms=roms, constants=constants)

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
