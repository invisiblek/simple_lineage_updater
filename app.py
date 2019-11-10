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

if "SOURCE_URL" in app.config:
  source_url = app.config['SOURCE_URL']
else:
  source_url = "https://github.com/invisiblek/simple_lineage_updater"
html_footer="<h3>Simple LineageOS Updater Server.<br/>Source <a href='" + source_url + "'>here</a>"

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
  c.execute("SELECT DISTINCT r.device, d.oem, d.name from rom r inner join device d on r.device = d.model order by r.device;")
  devices = c.fetchall()
  conn.commit()
  conn.close()

  h = "<html>"
  if "PAGE_BANNER" in app.config:
    h = h + "<h1>welcome to invisiblek's lineage updater server</h1>"
  else:
    h = h + "<h1>welcome to the updater server</h1>"
  h = h + "<ul>"
  for d in devices:
    h = h + "<li><a href='/" + d[0] + "'>" + d[0] + "</a> - " + d[1] + " " + d[2] + "</li>"
  h = h + "</ul>"
  h = h + html_footer
  h = h + "</html>"
  return h

@app.route('/<string:device>')
def device(device):
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  c.execute("SELECT r.filename, r.url, d.name, d.oem, d.model from rom r inner join device d on r.device = d.model where r.device = '" + device + "' order by r.filename;")
  roms = c.fetchall()
  conn.commit()
  conn.close()

  h = "<html>"
  if len(roms) > 0:
    h = h + "<h1>" + roms[0][3] + " " + roms[0][2] + " (" + roms[0][4] + ")</h1>"
  h = h + "<ul>"
  for r in roms:
    h = h + "<li><a href='" + r[1] + "'>" + r[0] + "</a></li>"
  h = h + "</ul>"
  h = h + html_footer
  h = h + "</html>"
  return h
