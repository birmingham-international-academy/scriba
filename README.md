# Scriba (English Academic Paraphrase Practice)

<img src="./badge-coverage.svg">

> A Canvas LTI for automated paraphrase analysis.

> Please note: if you encounter any problems setting up your environment contact us on ossedb@gmail.com

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

TODO

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

To generate the coverage badge run the following:

```
$ coverage-badge -o badge-coverage.svg
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
