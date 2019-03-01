FROM python:3.6

ENV PYTHONUNBUFFERED 1

ENV DOCKYARD /src
RUN mkdir ${DOCKYARD}
WORKDIR ${DOCKYARD}

### Install core packages
RUN apt-get -q -y update && apt-get upgrade -q -y && apt-get -q -y autoremove && apt-get -q -y autoclean
RUN apt-get install -q -y --no-install-recommends apt-utils
RUN apt-get install -q -y git default-jre supervisor

### Install Python packages
ADD requirements.txt ${DOCKYARD}/
RUN pip install -r requirements.txt
RUN pip install gunicorn gevent

### Setup
ADD . ${DOCKYARD}/
RUN python -m nltk.downloader wordnet wordnet_ic stopwords words punkt averaged_perceptron_tagger

### Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./docker-entrypoint.sh /

RUN ["chmod", "+x", "/docker-entrypoint.sh"]

ENTRYPOINT ["/docker-entrypoint.sh"]
# CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
