FROM java:jre-alpine

RUN apk add --update --no-cache \
	 unzip \
	 wget

ENV VERSION 4.3

RUN wget https://www.languagetool.org/download/LanguageTool-${VERSION}.zip
RUN unzip LanguageTool-${VERSION}.zip && \
    rm LanguageTool-${VERSION}.zip

WORKDIR /LanguageTool-${VERSION}

RUN export CLASSPATH="`find . -name '*.jar'`"

EXPOSE 8010

CMD java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8010 --public
