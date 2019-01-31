#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

source /elri/env_secrets_expand.sh

cmd="dockerize"

if [ "${DB_HOST}" != "" ]; then
    dockerize -wait tcp://${DB_HOST}:${DB_PORT}
fi

if [ "${SOLR_HOST}" != "" ]; then 
    dockerize -wait tcp://${SOLR_HOST}:${SOLR_PORT}
fi

python /elri/manage.py makemigrations accounts repository stats recommendations storage
python /elri/manage.py migrate
python /elri/manage.py rebuild_index --noinput
python /elri/manage.py collectstatic --noinput
#python /elri/manage.py createsuperuser --email elri@example.com --username admin --noinput 

if [ "${DEVELOPMENT}" != "" ]; then
    cmd="$cmd python /elri/manage.py runserver 0.0.0.0:8000 --insecure"
else
    cmd="$cmd gunicorn metashare.wsgi -b 0.0.0.0:8000 -w 4 --threads 8 --preload"
fi

$cmd