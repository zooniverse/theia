#!/bin/bash

echo Removing logs
rm tmp/*.log

echo Starting Celery
celery -A theia worker -l info

