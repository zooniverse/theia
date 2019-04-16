# theia
Planning the next-generation Floating Forests pipeline

## Etymology

Theia is the Greek goddess of sight and of the blue sky. She is the mother of the sun, the moon, and the dawn. Our hope is to use Theia to acquire satellite images and find blue skies!

## Tech

The proposed tech stack for Theia is:

* Django/GeoDjango
* Postgres
* Celery
* gdal
* Pillow
* Docker

## Getting started

### Docker environment

#### Build Image

Ensure that you have a modern-ish version of docker installed. Simply run

`docker build -t theia .` to build the image

If you have an image built, you can run it with:

`docker run theia`

#### Build Environment

To create the environment, including the postgres and redis servers and a web app and worker node

`docker-compose up &`

To, for exampe, create a second worker node

`docker-compose up --scale worker=2 &`

To halt instances

`docker-compose down`

Note that you can also remove the volumes (they will need to be recreated next time)

`docker-compose down -v`

### Local environment

Ensure that you have a modern python:

`brew install python`

and follow the installation notes to put the versionless alias on your `$PATH`.

Then install `pipenv` package and virtualization manager

`pip install pipenv`

Then use `pipenv` to install dependencies:

`pipenv install --dev`

Install GIS related dependencies:

`brew install postgis gdal`

Run Django app locally:

`pipenv run start_server`

### Accessing the app

The Django app can be accessed at http://localhost:8080/

### Running the tests

`pipenv run pytest`
