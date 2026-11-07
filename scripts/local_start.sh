#!/bin/bash
set -e

python3 ./db_versioning/db_versioning.py --mongo mongodb://mongodb:27017

exec python3 ./app/server.py -p
