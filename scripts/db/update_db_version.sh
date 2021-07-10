#!/bin/bash

set -e

db_url="`./scripts/db/get_db_ip.sh`:27017"

python3.8 db_versioning/db_versioning.py --mongo mongodb://$db_url
