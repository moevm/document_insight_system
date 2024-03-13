#! /bin/bash

set -e

VERSION_FILE_NAME="VERSION.json" # project directory

apache_config_filename=${1}
apache_ssl_mod=${2:-''}
#sudo scripts/setup_apache_config.sh $apache_config_filename $apache_ssl_mod

# generate version file
scripts/version.sh > app/$VERSION_FILE_NAME

mkdir -p ../slides_checker_mongo_data

docker-compose stop
docker-compose --project-name dis_test_build build --no-cache
docker-compose build

docker-compose up -d --remove-orphans
