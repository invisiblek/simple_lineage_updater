#!/bin/sh

cd app
FLASK_APP=main.py flask run --host=0.0.0.0
