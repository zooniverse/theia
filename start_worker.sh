#!/bin/bash

echo Removing logs
rm tmp/*.log

echo Starting Celery
exec celery -A theia worker -l info
