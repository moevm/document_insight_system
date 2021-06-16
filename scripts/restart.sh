#! /bin/bash

apache_config_filename=${1}
apache_ssl_mod=${2:-''}
sudo scripts/setup_apache_config.sh $apache_config_filename $apache_ssl_mod

mkdir -p ../slides_checker_mongo_data
docker-compose down --rmi local
docker-compose build --no-cache
docker-compose up -d --remove-orphans
