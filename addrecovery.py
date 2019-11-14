#!/usr/bin/env python3
#

import argparse
import os
import sqlite3
import sys

db_filename = "updater.db"

if not os.path.isfile(db_filename):
  print(db_filename + " does not exist! Aborting!")
else:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--md5sum", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--datetime", required=True)
    args = parser.parse_args()

    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute("DELETE FROM recovery where filename = '{0}';".format(args.filename))
    conn.commit()

    c.execute("INSERT INTO recovery (filename, device, md5sum, url, datetime) VALUES('{0}', '{1}', '{2}', '{3}', '{4}');".format(args.filename, args.device, args.md5sum, args.url, args.datetime))
    conn.commit()
    conn.close()
