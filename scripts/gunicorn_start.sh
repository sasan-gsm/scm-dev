#!/bin/bash

# Name of the application
NAME="scm"
# Django project directory
DJANGODIR=/app
# Number of worker processes
NUM_WORKERS=$(( 2 * $(nproc) + 1 ))
# WSGI module name
DJANGO_WSGI_MODULE=scm.wsgi
# Log level
LOG_LEVEL=info

echo "Starting $NAME as $(whoami)"

# Activate the virtual environment if using one
cd $DJANGODIR

# Start Gunicorn
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --bind=0.0.0.0:8000 \
  --log-level=$LOG_LEVEL \
  --log-file=/var/log/gunicorn/error.log \
  --access-logfile=/var/log/gunicorn/access.log \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --preload \
  --worker-class=sync