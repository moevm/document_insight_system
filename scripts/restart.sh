#! /bin/bash

set -e

VERSION_FILE_NAME="VERSION.json" # project directory
new_image="slides_checker_base_image"
old_image="slides_checker_base_image:old"

apache_config_filename=${1}
apache_ssl_mod=${2:-''}
scripts/setup_apache_config.sh $apache_config_filename $apache_ssl_mod

# generate version file
VERSION_FILE_PATH="$(dirname $(dirname $(readlink -f $0)))/$VERSION_FILE_NAME"
scripts/version.sh > $VERSION_FILE_PATH

# up docker
mkdir -p ../slides_checker_mongo_data
docker-compose down
docker tag $new_image $old_image
docker-compose build --no-cache 
docker rmi $old_image
docker-compose up -d --remove-orphans
