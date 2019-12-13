#!/usr/bin/env python3
#

import argparse
import os
import sqlite3
import sys

db_filename = "updater.db"

def delete(filename):
  if not os.path.isfile(db_filename):
    print(db_filename + " does not exist! Aborting!")
  else:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    c.execute("DELETE FROM rom where filename = '{0}';".format(filename))
    conn.commit()
    conn.close()

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--filename", required=True)
  args = parser.parse_args()

  delete(args.filename)
