# Scriba

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
- `DANDELION_API_KEY`: Text semantic similarity service offered by Dandelion (deprecated).

### 2. NLTK (Natural Language Toolkit) package

After installing the required packages, we need to download corpora that is used by NLTK:

```
$ ./bin/nltk_data.sh
```

### 3. NLTK Interface to the Stanford Parser

The Stanford Parser is a probabilistic parser written in Java. NLTK provides a Python interface to it;
so let's setup the Java environment:

```
$ sudo apt-get install default-jre
$ sudo apt-get install default-jdk
```

Then run `python bin/stanford_parser.py` to download and extract the Stanford parser.

### 4. SpaCy Package

Run the following command to download the 'en' model for SpaCy: `python -m spacy download en`

### 5. Language Tool

LanguageTool is a service that offers spell and grammar checking. Scriba adds it to its own grammar checking.

Run the following to get the Language Tool stable release as well as the ngram data (the total size of the unzipped files is about 15GB):

```
$ python bin/languagetool.py
```

This will download the necessary files in `lti_app/core/data/languagetool`.

### 6. Setup the Database

Todo.

### 7. Setup Redis

Redis is used as a storage for jobs from RQ (Redis Queue) for
queueing jobs and processing them in the background with
workers.

To setup Redis follow step 1 and 2 of this guide: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04.

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
Run the worker using:

```
$ python worker.py
```

### 3. Run the Language Tool Server

Language Tool is a rule-based grammar checker. Scriba's
grammar checker uses it as an added check.

To run the Language Tool server execute the following command:

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
2. `$ python manage.py migrate`
3. `$ python manage.py collectstatic`

In addition, if using the Digital Ocean setup described above, run:

```
$ sudo supervisorctl restart englishapp
```

## Testing

Run `pytest`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
