FROM java:jre-alpine

RUN apk add --update --no-cache \
	 unzip \
	 wget \
     supervisor

ENV VERSION 4.3

RUN wget https://www.languagetool.org/download/LanguageTool-${VERSION}.zip
RUN unzip LanguageTool-${VERSION}.zip && \
    rm LanguageTool-${VERSION}.zip
RUN mv LanguageTool-${VERSION} languagetool

WORKDIR /languagetool

RUN export CLASSPATH="`find . -name '*.jar'`"

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
