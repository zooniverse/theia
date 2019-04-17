#!/bin/bash

echo Applying migrations

python app/manage.py migrate --noinput

echo Starting Django server

python app/manage.py runserver 0:8080
