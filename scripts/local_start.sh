#! /bin/bash

python3 ./db_versioning/db_versioning.py --mongo mongodb://mongodb:27017

python3 ./app/server.py -p
