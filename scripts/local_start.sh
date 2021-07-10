#! /bin/bash

./scripts/db/update_db_version.sh
python3.8 ./app/server.py -p

