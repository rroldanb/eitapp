#!/bin/bash
set -e

# ── Wait for PostgreSQL ──
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Esperando PostgreSQL..."
    python -c "
import os, socket, time
url = os.environ['DATABASE_URL']
host = url.split('@')[1].split('/')[0].split(':')[0]
port = int(url.split('@')[1].split('/')[0].split(':')[1]) if ':' in url.split('@')[1].split('/')[0] else 5432
while True:
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        break
    except (OSError, socket.error):
        time.sleep(2)
print('✅ PostgreSQL disponible en', host, port)
    "
fi

python manage.py migrate --noinput

if [ "${DJANGO_DEBUG}" = "True" ]; then
    exec python manage.py runserver 0.0.0.0:${PORT:-8000}
else
    exec gunicorn transito_backend.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
fi
