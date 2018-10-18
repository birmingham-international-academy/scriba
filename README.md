# Scriba (English Academic Paraphrase Practice)

<img src="./badge-coverage.svg">

> A Canvas LTI for automated paraphrase analysis.

> Please note: if you encounter any problems when following this guide do not hesitate to contact us on ossedb@gmail.com

## How to read this document

### I want to setup a new local development environment on my machine

- [General Setup](general-setup)
- [Development Setup](development-setup)

### I want to setup a new production machine on DigitalOcean

- [DigitalOcean Setup](digitalocean-setup)
- [General Setup](general-setup)

### I want to deploy to an existing production instance on DigitalOcean

- [Deployment Routine](#routine)

## General Setup

Scriba is compatible with Python 3.5.2.

First of all `git clone` this repository and install the dependencies using: `pip install -r requirements.txt`.

### 1. Environment Settings

Create a `.env` file resembling the `.env.example` file in the same directory (`scriba/settings`).

Then set the keys appropriately:
- `SECRET_KEY`: Django secret key.
- `CANVAS_CONSUMER_KEY`: Canvas consumer key for LTI communication. This can be generated as a 256-bit key.
- `CANVAS_SHARED_SECRET`: Canvas consumer/shared secret for LTI communication. This can be generated as a 256-bit key.

### 2. NLTK (Natural Language Toolkit) package

After installing the required packages, we need to download corpora that is used by NLTK:

```
./bin/nltk_data.sh
```

### 3. The Stanford CoreNLP Package

The Stanford CoreNLP package contains the Stanford parser which is a probabilistic parser written in Java.
In order to use it, let's setup the Java environment:

```
sudo apt-get install default-jre
sudo apt-get install default-jdk
```

Then run `python -m bin.stanford_corenlp` to download and extract the Stanford parser.

### 4. Language Tool

LanguageTool is a service that offers spell and grammar checking. Scriba adds it to its own grammar checking.

Run the following to get the Language Tool stable release as well as the ngram data (the total size of the unzipped files is about 15GB):

```
python bin.languagetool
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
sudo apt-get update
sudo apt-get install memcached
sudo apt-get install libmemcached-tools
```

Then install the pylibmc interface:

```
sudo apt-get install -y libmemcached-dev zlib1g-dev libssl-dev python-dev build-essential
pip install pylibmc
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
pip install django-sslserver
```

Then run the server using:

```
python manage.py runsslserver --settings=scriba.settings.local
```

### 2. Run the Worker

Scriba uses Python RQ for background tasks management.
Run the worker locally using:

```
python manage.py rqworker default
```

### 3. Run the Stanford CoreNLP Server

The following command will run the CoreNLP Server on port `9000`:

```
java -mx4g -cp "lti_app/core/data/stanford-corenlp/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
```

### 4. Run the Language Tool Server

Language Tool is a rule-based grammar checker. Scriba's
grammar checker uses it as an added check.

To run the Language Tool server on port `8081` execute the following command:

```
java -cp lti_app/core/data/languagetool/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --languageModel lti_app/core/data/languagetool/ngram
```

## Production Setup

If you are setting a new DigitalOcean machine then follow the next section otherwise skip to [Routine](#routine).

### DigitalOcean Setup

This step is done only when we need a new machine on DigitalOcean, otherwise skip to the next section.

#### Create a New Droplet

Go into the DigitalOcean dashboard and create a droplet with the appropriate settings.

#### Installing the server dependencies

After creating the server run `ssh <username>@<ip address>`.

Then upgrade the packages:

```
sudo apt-get update
sudo apt-get -y upgrade
```

##### PostgreSQL

Install the dependencies to use PostgreSQL with Python/Django:

```
sudo apt-get -y install build-essential libpq-dev python-dev
```

Install the PostgreSQL Server:

```
sudo apt-get -y install postgresql postgresql-contrib
```

##### NGINX

Install NGINX, which will be used to serve static assets (css, js, images) and also to run the Django application behind a proxy server:

```
sudo apt-get -y install nginx
```

##### Supervisor

Supervisor will start the application server and manage it in case of server crash or restart:

```
sudo apt-get -y install supervisor
```

Enable and start the Supervisor:

```
sudo systemctl enable supervisor
sudo systemctl start supervisor
```

##### Python Virtualenv

The Django application will be deployed inside a Python Virtualenv, for a better requirements management:

```
sudo apt-get -y install python-virtualenv
```

#### Configure PostgreSQL Database

Switch users:

```
su - postgres
```

Create a database user and the application database:

```
createuser englishapp
createdb englishapp --owner englishapp
psql -c "ALTER USER englishapp WITH PASSWORD 'mypassword'"
```

PS: Make sure to pick a secure password!

We can now go back to the root user, simply exit:

```
exit
```

#### Configure The Application User

Create a new user with the command below:

```
adduser englishapp
```

Add the user to the list of sudoers:

```
gpasswd -a englishapp sudo
```

Switch to the recently created user:

```
su - englishapp
```

#### Configure the Python Virtualenv

At this point we are logged in with the englishapp user (or whatever named you selected). We will install our Django application in this user's home directory /home/englishapp:

```
virtualenv .
```

Activate it:

```
source bin/activate
```

Clone the repository:

```
git clone https://github.com/birmingham-international-academy/scriba
```

#### Configure Gunicorn

First install Gunicorn inside the virtualenv:

```
pip install gunicorn
```

Create a file named gunicorn_start inside the `bin/` folder:

```
nano bin/gunicorn_start
```

And add the following information and save it (`/home/englishapp/bin/gunicorn_start`):

```
#!/bin/bash

NAME="englishapp"
DIR=/home/englishapp/scriba
USER=englishapp
GROUP=englishapp
WORKERS=3
BIND=unix:/home/englishapp/run/gunicorn.sock
DJANGO_SETTINGS_MODULE=scriba.settings.production
DJANGO_WSGI_MODULE=scriba.wsgi
LOG_LEVEL=error

cd $DIR
source ../bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DIR:$PYTHONPATH

exec ../bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=-
```

Make the `gunicorn_start` file is executable:

```
chmod u+x bin/gunicorn_start
```

In the home directory create a directory named run, for the unix socket file:

```
mkdir run
```

#### Configure Supervisor

Now what we want to do is configure Supervisor to take care of running the gunicorn server, the worker,
the CoreNLP server, and the LanguageTool server.

First let's create a folder named logs inside the virtualenv:

```
mkdir logs
```

Create the log files:

```
cd logs
touch gunicorn.log languagetool.log  nginx-access.log  nginx-error.log  stanford_corenlp.log  worker.log
```

##### Supervisor configuration for the web server

Create a Supervisor configuration file for the web server:

```
sudo vim /etc/supervisor/conf.d/englishapp.conf
```

with the following contents:

```
[program:englishapp]
command=/home/englishapp/bin/gunicorn_start
user=englishapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/englishapp/logs/gunicorn.log
stdout_logfile_maxbytes=5MB
```

##### Supervisor configuration for the worker

Create a Supervisor configuration file for the worker:

```
sudo vim /etc/supervisor/conf.d/worker.conf
```

with the following contents:

```
[program:worker]
command=/home/englishapp/bin/python manage.py rqworker default
directory=/home/englishapp/scriba
user=englishapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/englishapp/logs/worker.log
stdout_logfile_maxbytes=5MB
```

##### Supervisor configuration for Stanford CoreNLP

Create a Supervisor configuration file for Stanford CoreNLP:

```
sudo vim /etc/supervisor/conf.d/stanford_corenlp.conf
```

with the following contents:

```
[program:stanford_corenlp]
command=java -mx4g -cp "lti_app/core/data/stanford-corenlp/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
directory=/home/englishapp/scriba
user=englishapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/englishapp/logs/stanford_corenlp.log
stdout_logfile_maxbytes=5MB
```

##### Supervisor configuration for LanguageTool

Create a Supervisor configuration file for LanguageTool:

```
sudo vim /etc/supervisor/conf.d/languagetool.conf
```

with the following contents:

```
[program:languagetool]
command=java -cp lti_app/core/data/languagetool/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --languageModel lti_app/core/data/languagetool/ngram
directory=/home/englishapp/scriba
user=englishapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/englishapp/logs/languagetool.log
stdout_logfile_maxbytes=5MB
```

##### Wrap up

Reread Supervisor configuration files and make the new program available:

```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart englishapp
sudo supervisorctl restart worker
sudo supervisorctl restart stanford_corenlp
sudo supervisorctl restart languagetool
```

#### Configure NGINX

> Note: contact ossedb@gmail.com for this step.

Add a new configuration file named urban inside `/etc/nginx/sites-available/`:

```
sudo nano /etc/nginx/sites-available/englishapp.tk
```

with the following contents:

```
upstream app_server {
    server unix:/home/englishapp/run/gunicorn.sock fail_timeout=0;
}

# Redirect all non-encrypted to encrypted
server {
    server_name englishapp.tk www.englishapp.tk;
    listen 80;
    return 301 https://englishapp.tk$request_uri;
}

server {
    server_name englishapp.tk www.englishapp.tk;

    listen 443;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/englishapp.tk/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/englishapp.tk/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

    client_max_body_size 4G;

    access_log /home/englishapp/logs/nginx-access.log;
    error_log /home/englishapp/logs/nginx-error.log;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;  # <-
        proxy_set_header Host $http_host;
        proxy_redirect off;

        if (!-f $request_filename) {
            proxy_pass http://app_server;
            break;
        }
    }
}
```

Create a symbolic link to the sites-enabled dir:

```
sudo ln -s /etc/nginx/sites-available/englishapp.tk /etc/nginx/sites-enabled/englishapp.tk
```

Remove NGINX default website:

```
sudo rm /etc/nginx/sites-enabled/default
```

Restart NGINX:

```
sudo service nginx restart
```

### Routine

Whenever local changes are made the server must always perform the following:

1. In your local machine run: `ssh <username>@<ip address>`. For the current DigitalOcean setup the values are `<username> = englishapp` and `<ip address> = 178.128.41.130`.
2. Then in the server run the following commands:
    1. `$ git pull origin master`
    2. `$ python manage.py migrate` if changes to the migrations have been made
    3. `$ python manage.py collectstatic` if changes to static files have been made
    4. `$ sudo supervisorctl restart englishapp` to restart the server
    5. `$ sudo supervisorctl restart worker` to restart the worker

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
