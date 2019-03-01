#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start supervisord
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf