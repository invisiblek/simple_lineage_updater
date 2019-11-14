#!/usr/bin/env python3

import os
import sqlite3
import sys

from datetime import datetime

db_filename = "updater.db"

devices = False
roms = False

if not os.path.isfile(db_filename):
  conn = sqlite3.connect(db_filename)
  c = conn.cursor()
  c.execute("CREATE TABLE device(id INTEGER PRIMARY KEY AUTOINCREMENT, model TEXT, oem TEXT, name TEXT);")
  c.execute("CREATE TABLE rom(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, datetime INTEGER, device TEXT, version TEXT, romtype TEXT, md5sum TEXT, romsize INTEGER, url TEXT);")
  c.execute("CREATE TABLE recovery(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, datetime INTEGER, device TEXT, md5sum TEXT, url TEXT);")
  conn.commit()
  conn.close()
  devices = True

if len(sys.argv) > 1 and sys.argv[1] == "devices":
  devices = True

if devices:
  if not os.path.isfile("devices.txt"):
    print("No devices.txt! Aborting!")
  else:
    print("Generating device table...")
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute("DELETE FROM device;")
    conn.commit()
    with open("devices.txt") as f:
      line = f.readline()
      while line:
        e = line.rstrip().split('|')
        c.execute("INSERT INTO device (name, model, oem) VALUES('{0}', '{1}', '{2}');".format(e[0], e[1], e[2]))
        line = f.readline()
    conn.commit()
    conn.close()
