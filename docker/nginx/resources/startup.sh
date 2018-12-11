#!/bin/bash

source /env_secrets_expand.sh

cmd="dockerize"

if [ "$ELRI_NODES" != "" ]; then
    for node in ${ELRI_NODES}; do
		cmd="$cmd -wait http://${node} -wait-http-header X-Forwarded-Proto:http"
	done
fi

cmd="$cmd -template /etc/nginx/conf.d/vhost.tmpl:/etc/nginx/conf.d/vhost.conf"
cmd="$cmd -timeout 240s nginx"

$cmd