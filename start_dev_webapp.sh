#!/bin/bash

source venv/bin/activate
cd solr
../metashare/stop-solr.sh
pwd
nohup java -Djetty.port=8983 -DSTOP.PORT=8079 -DSTOP.KEY=stopkey -jar start.jar > webapp_solr_log.out 2> webapp_solr_log.err &

cd ..
sleep 8 # give SOLR time to start up before trying to verify that it is there

#python manage.py runserver 0.0.0.0:4004 --insecure > webapp_log.out 2> webapp_log.err &
python manage.py runserver 0.0.0.0:4004 --insecure

deactivate


