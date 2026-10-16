#! /bin/bash

set -e

make sync-version

apache_config_filename=${1}
apache_ssl_mod=${2:-''}
#sudo scripts/setup_apache_config.sh $apache_config_filename $apache_ssl_mod

mkdir -p ../slides_checker_mongo_data

docker-compose stop
docker-compose --project-name dis_test_build build --no-cache
docker-compose build

docker-compose up -d --remove-orphans
