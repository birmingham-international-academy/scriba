FROM java:jre-alpine

RUN apk add --update --no-cache \
	 unzip \
	 wget

ENV URL http://nlp.stanford.edu/software
ENV VERSION 2018-02-27

RUN wget ${URL}/stanford-corenlp-full-${VERSION}.zip
RUN unzip stanford-corenlp-full-${VERSION}.zip && \
	rm stanford-corenlp-full-${VERSION}.zip

WORKDIR /stanford-corenlp-full-${VERSION}

RUN wget ${URL}/stanford-srparser-2014-10-23-models.jar

RUN export CLASSPATH="`find . -name '*.jar'`"

EXPOSE 9000

CMD java -cp "*" -mx4g edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 15000
