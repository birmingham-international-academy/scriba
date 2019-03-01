# Scriba (English Academic Paraphrase Practice)

> A Canvas LTI for automated paraphrase analysis.

> Please note: if you encounter any problems setting up your environment contact us on o.edbali@bham.ac.uk or r.nickalls@birmingham.ac.uk

## Development Setup

Clone the project:

```
git clone https://github.com/birmingham-international-academy/scriba.git
```

Before installing the development environment we need to set the appropriate environment variables.

### Environment Settings

#### app

In the `app` directory create a `.env` file resembling the `.env.example` file in the same directory.

Then set the keys appropriately:
- `SECRET_KEY`: Django secret key.
- `CANVAS_CONSUMER_KEY`: Canvas consumer key for LTI communication. This can be generated as a 256-bit key.
- `CANVAS_SHARED_SECRET`: Canvas consumer/shared secret for LTI communication. This can be generated as a 256-bit key.

#### db

In the `db` directory create a `.env` file resembling the `.env.example` file in the same directory.

The values defined here must resemble those defined in the `app` section:

- `POSTGRES_DB` -> `DB_NAME`
- `POSTGRES_USER` -> `DB_USER`
- `POSTGRES_PASSWORD` -> `DB_PASSWORD`

#### nginx

For development the Nginx `HOST` variable must be `localhost`.

### Run Docker

> Note: you may need to run `sudo` before each Docker command.

If you're building the app for the first time then run the following:

```
docker-compose build --build-arg env=dev
```

This operation will take at least 10 minutes for building the necessary images.

For subsequent uses, run:

```
docker-compose up
```

After this you can access the app using: https://127.0.0.1

Note: you must use `https`.

### Deleting Everything

If you want to delete all images, containers, and volumes created by Docker run the following:

```
docker rm $(docker ps -a -q) --force
docker volume prune
docker rmi $(docker images -q) --force
```

### Inspecting the Logs

To inspect the logs on any container run the following:

```
docker logs <container_id>
```

where `<container_id>` can be retrieved from the list given by `docker ps`.

## Setting up the LTI on Canvas

### Register the development LTI

To register the development LTI go into `Settings > Apps > View App Configurations > + App`.

This will prompt a popup:

- **Configuration Type**: choose *Paste XML*
- **Name**: give a meaningful name to the app (e.g. English APP - DEV)
- **Consumer key**: the consumer key used in the `.env` file.
- **Shared secret**: the shared secret used in the `.env` file.
- **XML Configuration**
    * For this you need to enter in the browser: `https://127.0.0.1/register`
    * This will return an XML response which you need to copy
    * Paste the XML in the text area in the popup
    * Change any `http://127.0.0.1/launch` string to use `https` instead (if not already)

### Create an assignment using the LTI

- In the **Submission type** entry choose **External tool** and *find* the newly created LTI (or an existing one).
- Click **Save** or **Save & publish**

## Production Setup

TODO

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
