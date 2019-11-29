FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8

MAINTAINER dcd <dcd1182@gmail.com>

RUN pip install flask flask_compress

COPY ./app /app

RUN cd /app && \
    python /app/initial_setup.py

EXPOSE 80
