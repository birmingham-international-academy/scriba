#!/usr/bin/env bash

if [[ $env == "prod" ]]; then
    echo "Production setup not yet implemented!"
else
    openssl req -subj '/CN=localhost' -x509 -newkey rsa:4096 -nodes -keyout /etc/nginx/conf.d/key.pem -out /etc/nginx/conf.d/cert.pem -days 365
fi

# envsubst < /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'

exec nginx -g 'daemon off;'
