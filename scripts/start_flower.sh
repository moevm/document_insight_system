#!/bin/sh
set -eu

# Flower adds its own slash before each route. Accept /, flower and /flower/.
prefix=${FLOWER_PREFIX:-}
while [ "${prefix#/}" != "$prefix" ]; do prefix=${prefix#/}; done
while [ "${prefix%/}" != "$prefix" ]; do prefix=${prefix%/}; done

exec celery --broker="${CELERY_BROKER:?CELERY_BROKER is required}" flower \
    --port=5555 \
    --url_prefix="$prefix" \
    --basic_auth="${FLOWER_BASIC_AUTH:?FLOWER_BASIC_AUTH is required}" \
    --persistent=True \
    --db=/etc/db/flower
