#! /bin/bash
VERSION_FILE_NAME="VERSION.json" # project directory

apache_config_filename=${1}
apache_ssl_mod=${2:-''}
sudo scripts/setup_apache_config.sh $apache_config_filename $apache_ssl_mod

# generate version file
VERSION_FILE_PATH="$(dirname $(dirname $(readlink -f $0)))/$VERSION_FILE_NAME"
scripts/version.sh > $VERSION_FILE_PATH

# up docker
mkdir -p ../slides_checker_mongo_data
docker-compose down
docker-compose build --no-cache
docker-compose up -d --remove-orphans
