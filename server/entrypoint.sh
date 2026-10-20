#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py shell -c "from djangoapp.populate import initiate; initiate()"
exec gunicorn djangoproj.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
