#! /bin/bash

python3.8 ./db_versioning/db_versioning.py --mongo mongodb://mongodb:27017

python3.8 ./app/server.py -p
