#!/bin/bash

source /env_secrets_expand.sh

cmd="dockerize"

if [ "$ELRI_NODES" != "" ]; then
    for node in ${ELRI_NODES}; do
		cmd="$cmd -wait http://${node} -wait-http-header X-Forwarded-Proto:http"
	done
fi

pushd /tmp

case "${ELRI_PROTOCOL}" in
	"https")
		for file in https-*.tmpl; do
			filename=`echo ${file} | cut -d '.' -f 1`
			extension=`echo ${file} | cut -d '.' -f 2`
			cmd="$cmd -template /tmp/${file}:/etc/nginx/conf.d/${filename}.conf"
		done
		;;
	"http")
		for file in http-*.tmpl; do
			filename=`echo ${file} | cut -d '.' -f 1`
			extension=`echo ${file} | cut -d '.' -f 2`
			cmd="$cmd -template /tmp/${file}:/etc/nginx/conf.d/${filename}.conf"
		done
		;;
	*)
		printf "Protocol option does not exist or is not set: %s" "${ELRI_PROTOCOL}"
		;;
esac

popd

cmd="$cmd -template /tmp/security-vhost.tmpl:/etc/nginx/conf.d/security.conf"
cmd="$cmd -timeout 240s nginx"

$cmd
