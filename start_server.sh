#!/bin/bash

while ! nc -z postgres 5432; do
  echo Waiting for Postgres
  sleep 3
done

echo Applying migrations

python manage.py migrate --noinput

echo Starting Django server

python manage.py runserver 0:8080
