#! /bin/bash

set -e

VERSION_FILE_NAME="VERSION.json" # project directory
new_image="slides_checker_base_image"
old_image="slides_checker_base_image:old"

apache_config_filename=${1}
apache_ssl_mod=${2:-''}
#sudo scripts/setup_apache_config.sh $apache_config_filename $apache_ssl_mod

# generate version file
scripts/version.sh > app/$VERSION_FILE_NAME

# up docker
mkdir -p ../slides_checker_mongo_data

result=$( docker images --filter=reference="$new_image" -q )

# if docker images exits
if [[ -n "$result" ]]; then
    docker-compose down
    docker tag $new_image $old_image
fi
docker-compose build --no-cache 
docker rmi -f $old_image
docker-compose up -d --remove-orphans
