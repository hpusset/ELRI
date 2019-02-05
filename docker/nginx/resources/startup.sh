#!/bin/bash

source /env_secrets_expand.sh

cmd="dockerize"

if [ "$ELRI_NODES" != "" ]; then
    for node in ${ELRI_NODES}; do
		cmd="$cmd -wait http://${node} -wait-http-header X-Forwarded-Proto:http"
	done
fi

pushd /tmp

for file in *.tmpl; do
	filename=`echo ${file} | cut -d '.' -f 1`
	extension=`echo ${file} | cut -d '.' -f 2`
	cmd="$cmd -template /tmp/${file}:/etc/nginx/conf.d/${filename}.conf"
done

popd

cmd="$cmd -timeout 240s nginx"

$cmd