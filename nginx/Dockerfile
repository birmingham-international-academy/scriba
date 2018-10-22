FROM nginx:latest

ARG env=dev

RUN apt-get -q -y update && apt-get -q -y upgrade && apt-get -q -y install libssl-dev openssl

RUN rm -f /etc/nginx/conf.d/*
COPY *.conf /etc/nginx/conf.d/
COPY install.sh /scripts/install.sh
RUN chmod +x /scripts/install.sh

CMD ["/bin/bash", "/scripts/install.sh"]
