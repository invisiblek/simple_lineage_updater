#!/usr/bin/env python3
#

import argparse
import os
import sqlite3
import sys

db_filename = "updater.db"

def add(filename, device, version, romtype, md5, romsize, url, dt):
  if not os.path.isfile(db_filename):
    print(db_filename + " does not exist! Aborting!")
  else:
      conn = sqlite3.connect(db_filename)
      c = conn.cursor()
      c.execute("DELETE FROM rom where filename = '{0}';".format(filename))
      conn.commit()

      c.execute("INSERT INTO rom (filename, device, version, romtype, md5sum, romsize, url, datetime) VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}');".format(filename, device, version, romtype, md5, romsize, url, dt))
      conn.commit()
      conn.close()

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
