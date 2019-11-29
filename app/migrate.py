#!/usr/bin/env python3
#
# For devices, the file device.txt (included) should have lines in the following format:
#   <pretty name>|<codename>|<oem>
# Example:
#   Pixel 3a XL|bonito|Google
#
# For roms, the roms.txt (not included) should have lines in the following format:
#   <filename>|<codename>|<version>|<romtype>|<md5sum>|<romsize>|<url>|<datetime>
# Example:
#   lineage-17.0-20191104-UNOFFICIAL-bonito.zip|bonito|17.0|unofficial|4a965a452e46e58fd8cb4fd3c4b5346b|1069177523|https://someplace.com/bonito/releases/download/lineage-17.0-20191104-UNOFFICIAL-bonito/lineage-17.0-20191104-UNOFFICIAL-bonito.zip|2019-11-04T17:36:23.000+00:00
#

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
  c.execute("CREATE TABLE recovery(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, device TEXT, url TEXT);")
  conn.commit()
  conn.close()
  devices = True
  roms = True

if len(sys.argv) > 1 and sys.argv[1] == "devices":
  devices = True

if len(sys.argv) > 1 and sys.argv[1] == "roms":
  roms = True

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

if roms:
  if not os.path.isfile("roms.txt"):
    print("No roms.txt! Skipping...")
  else:
    print("Generating rom table...")
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute("DELETE FROM rom;")
    conn.commit()
    with open("roms.txt") as f:
      line = f.readline()
      while line:
        e = line.rstrip().split('|')
        c.execute("INSERT INTO rom (filename, device, version, romtype, md5sum, romsize, url, datetime) VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}');".format(e[0], e[1], e[2], e[3], e[4], e[5], e[6], datetime.fromisoformat(e[7]).timestamp()))
        line = f.readline()
    conn.commit()
    conn.close()
