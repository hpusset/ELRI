#!/bin/bash



cd solr
../metashare/stop-solr.sh
cd ..

echo $PWD

pid=`ps -ef | grep "$PWD/venv/bin/python manage.py runserver 0.0.0.0:4004 --insecure" | grep -v grep | awk '{print $2}'`

echo $pid
kill -9 $pid

