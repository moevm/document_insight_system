#!/bin/bash

set -e

container_id=`docker ps --quiet --filter "ancestor=mongo:4.0.17-xenial" --filter "name=slide"`
container_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${container_id}`

echo ${container_ip}
