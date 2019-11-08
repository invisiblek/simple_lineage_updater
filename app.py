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
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  c.execute("SELECT DISTINCT device from rom order by device;")
  devices = c.fetchall()
  conn.commit()
  conn.close()

  h = "<html><ul>"
  for d in devices:
    h = h + "<li><a href='/" + d[0] + "'>" + d[0] + "</a></li>"
  h = h + "</ul></html>"
  return h

@app.route('/<string:device>')
def device(device):
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  c.execute("SELECT filename, url from rom where device = '" + device + "' order by filename;")
  roms = c.fetchall()
  conn.commit()
  conn.close()

  h = "<html><ul>"
  for r in roms:
    h = h + "<li><a href='" + r[1] + "'>" + r[0] + "</a></li>"
  h = h + "</ul></html>"
  return h
