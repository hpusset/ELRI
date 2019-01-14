#!/bin/bash

source /env_secrets_expand.sh

cmd="docker-entrypoint.sh"

cmd="$cmd postgres"

$cmd