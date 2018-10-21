#!/usr/bin/env sh

python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --reload --certfile=compose_local/localhost.crt --keyfile=compose_local/localhost.key --bind :443 scriba.wsgi:application
