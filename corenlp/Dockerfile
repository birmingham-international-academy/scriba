FROM java:jre-alpine

RUN apk add --update --no-cache \
	 unzip \
	 wget \
	 supervisor

ENV URL http://nlp.stanford.edu/software
ENV VERSION 2018-02-27

RUN wget ${URL}/stanford-corenlp-full-${VERSION}.zip
RUN unzip stanford-corenlp-full-${VERSION}.zip && \
	rm stanford-corenlp-full-${VERSION}.zip
RUN mv stanford-corenlp-full-${VERSION} corenlp

WORKDIR /corenlp

RUN wget ${URL}/stanford-srparser-2014-10-23-models.jar
RUN export CLASSPATH="`find . -name '*.jar'`"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
