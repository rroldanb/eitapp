#!/bin/bash
set -e

python manage.py migrate --noinput

if [ "${DJANGO_DEBUG}" = "True" ]; then
    exec python manage.py runserver 0.0.0.0:${PORT:-7860}
else
    exec gunicorn transito_backend.wsgi --bind 0.0.0.0:${PORT:-7860} --workers 2
fi
