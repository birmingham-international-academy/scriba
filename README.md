# Scriba (English Academic Paraphrase Practice)

<img src="./badge-coverage.svg">

> A Canvas LTI for automated paraphrase analysis.

## General Setup

Scriba is compatible with Python 3.5.2.

> Please note: if you encounter any problems when following this guide do not hesitate to contact us on ossedb@gmail.com

First of all install the dependencies using: `pip -r requirements.txt`.

### 1. Environment Settings

Create a `.env` file resembling the `.env.example` file in the same directory (`scriba/settings`).

Then set the keys appropriately:
- `SECRET_KEY`: Django secret key.
- `CANVAS_CONSUMER_KEY`: Canvas consumer key for LTI communication. This can be generated as a 256-bit key.
- `CANVAS_SHARED_SECRET`: Canvas consumer/shared secret for LTI communication. This can be generated as a 256-bit key.
- `CANVAS_DEVELOPER_KEY`: Canvas API key.

### 2. NLTK (Natural Language Toolkit) package

After installing the required packages, we need to download corpora that is used by NLTK:

```
$ ./bin/nltk_data.sh
```

### 3. The Stanford CoreNLP Package

The Stanford CoreNLP package contains the Stanford parser which is a probabilistic parser written in Java.
In order to use it, let's setup the Java environment:

```
$ sudo apt-get install default-jre
$ sudo apt-get install default-jdk
```

Then run `python -m bin.stanford_corenlp` to download and extract the Stanford parser.

### 4. Language Tool

LanguageTool is a service that offers spell and grammar checking. Scriba adds it to its own grammar checking.

Run the following to get the Language Tool stable release as well as the ngram data (the total size of the unzipped files is about 15GB):

```
$ python bin.languagetool
```

This will download the necessary files in `lti_app/core/data/languagetool`.

### 5. Setup the Database

Follow this tutorial up to "Opening a Postgres Prompt with the New Role" (included):

https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-18-04

Then update the `.env` file with the `DB_NAME`, `DB_USER` and `DB_PASSWORD` variables.

`DB_HOST` is usually `127.0.0.1` and `DB_PORT` is 5432 (see these default values in `.env.example`).

### 6. Setup Redis

Redis is used as a storage for jobs from RQ (Redis Queue) for
queueing jobs and processing them in the background with
workers.

To setup Redis follow step 1 and 2 of this guide: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04.

### 7. Memcached

Install Memcached from the official repositories:

```
$ sudo apt-get update
$ sudo apt-get install memcached
$ sudo apt-get install libmemcached-tools
```

Then install the pylibmc interface:

```
$ sudo apt-get install -y libmemcached-dev zlib1g-dev libssl-dev python-dev build-essential
$ pip install pylibmc
```

Next we need to increase the size of
the cache entries. To do so, open `/etc/memcached.conf` and add the following line `-I 128M`.

## Development Setup

The following steps must be executed
after the general setup if you
are using a development setup.

### 1. Run the Server in Development Mode

To run a local HTTPS server you have to install the following Django app:

```
$ pip install django-sslserver
```

Then run the server using:

```
$ python manage.py runsslserver --settings=scriba.settings.local
```

### 2. Run the Worker

Scriba uses Python RQ for background tasks management.
Run the worker locally using:

```
$ python manage.py rqworker default
```

### 3. Run the Stanford CoreNLP Server

The following command will run the CoreNLP Server on port `9000`:

```
$ java -mx4g -cp "lti_app/core/data/stanford-corenlp/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
```

### 4. Run the Language Tool Server

Language Tool is a rule-based grammar checker. Scriba's
grammar checker uses it as an added check.

To run the Language Tool server on port `8081` execute the following command:

```
$ java -cp lti_app/core/data/languagetool/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --languageModel lti_app/core/data/languagetool/ngram
```

## Production Setup

The following steps must be executed
after the general setup if you
are using a production setup (here we
are using DigitalOcean).

### 1. DigitalOcean Setup

Todo.

### Routine

Whenever local changes are made the server must always perform the following:

1. `$ git pull origin master`
2. `$ python manage.py migrate` if changes to the migrations have been made
3. `$ python manage.py collectstatic` if changes to static files have been made

In addition, if using the Digital Ocean setup described above, run:

```
$ sudo supervisorctl restart englishapp
$ sudo supervisorctl restart worker
```

This will restart the WSGI HTTP server and the Django worker.

## Testing

Before starting the tests you must have the
Stanford CoreNLP server running (see above).

Then run `pytest`.

To run individual tests (say grammar checking):

```
pytest lti_app/tests/grammar_checker/test_grammar_checker.py
```

### Coverage

Test coverage is a useful tool for
finding untested parts of a codebase.

To view the test coverage report run
the following command:

```
$ pytest --cov
```

To generate the coverage badge run the following:

```
$ coverage-badge -o badge-coverage.svg
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
