# theia
Planning the next-generation Floating Forests pipeline

## Etymology

Theia is the Greek goddess of sight and of the blue sky. She is the mother of the sun, the moon, and the dawn. Our hope is to use Theia to acquire satellite images and find blue skies!

## Tech

The proposed tech stack for Theia is:

* Django / GeoDjango
* Django REST Framework
* Requests / Requests OAuth
* Postgres
* Celery
* gdal
* Pillow
* Docker / Kubernetes

## Getting started

### Docker environment

Ensure that you have docker & docker-compose installed.

Then run

`docker-compose build` to build the image

To create the environment, including the postgres and redis servers and a web app and worker node

`docker-compose up -d`

To, for example, create a second worker node

`docker-compose up --scale worker=2 -d`

To halt instances

`docker-compose down`

Note that you can also remove the volumes (they will need to be recreated next time)

`docker-compose down -v`

To develop in the docker containers via bash
`docker-compose run --rm --service-ports app bash`

this will provide you with access to python, libraries and all dependent services needed for development, e.g. from the bash console run:
`pytest` to test the application
setup local databases
`pipenv run create_local_db`
`pipenv run drop_local_db`
Run Django app locally (applying migrations if necessary):
`pipenv run server`
Run the Celery worker locally (does not apply migrations):
`pipenv run worker`

### Local environment

Make sure that you have an entry in your `/etc/hosts` file that looks like this:

`127.0.0.1  postgres`

so that we can find the postgres server when the app is running locally

Install the correct version of postgres:

`brew install postgresql@9.4`

If you already had a postgres install, you should be able to select your postgres version this way:

`brew switch postgresql 9.4`

If not, you can also use this keg-only formula by force-linking it:

`brew link postgresql@9.4 --force`

Add the user `theia` with password `theia`:

`createuser theia -d -P`

Make sure that you have an entry in your `/etc/hosts` file that looks like this:

`127.0.0.1 redis`

so that we can find the redis server when the app is running locally

Install the current version of redis:

`brew install redis`

Ensure that you have a modern python:

`brew install python`

and follow the installation notes to put the versionless alias on your `$PATH`.

Then install `pipenv` package and virtual environment manager

`pip install pipenv`

Then use `pipenv` to install dependencies:

`pipenv install --dev`

Install GIS related dependencies:

`brew install postgis gdal`

Install other related dependencies:

`brew install libtiff`

To drop or create the local DB that theia will be using:

`pipenv run create_local_db`

`pipenv run drop_local_db`

Run Django app locally (applying migrations if necessary):

`pipenv run server`

Run the Celery worker locally (does not apply migrations):

`pipenv run worker`

- If you find yourself running into the following error while attempting to run the above:

```
File "/Users/chelseatroy/.pyenv/versions/3.7.4/lib/python3.7/ssl.py", line 98, in <module>
    import _ssl             # if we can't import it, let the error propagate
ImportError: dlopen(/Users/chelseatroy/.local/share/virtualenvs/theia-LYdUFkJN/lib/python3.7/lib-dynload/_ssl.cpython-37m-darwin.so, 2): Library not loaded: /usr/local/opt/openssl/lib/libssl.1.0.0.dylib
  Referenced from: /Users/chelseatroy/.local/share/virtualenvs/theia-LYdUFkJN/lib/python3.7/lib-dynload/_ssl.cpython-37m-darwin.so
  Reason: image not found
```
You can follow the instructions [here](https://mithun.co/hacks/library-not-loaded-libcrypto-1-0-0-dylib-issue-in-mac/).

### Accessing the app

Regardless of whether you're running it locally or inside the image, the Django app can be accessed at http://localhost:8080/

### Running the tests

Locally:

Make sure that you have done all of the above, and if you have never run the server you may also need to run the migrations:

`pipenv run migrate`

and then you can run the tests with

`pipenv run tests`

In the container:
`docker-compose run --rm app bash`

Then from the bash shell in the container
`python manage.py migrate` setup the db
`pytest --cov=theia` run the tests
