#!/bin/bash

db_name="dis-db"

db_url="`./scripts/db/get_db_ip.sh`:27017"

./scripts/db/mongo.sh -H ${db_url} ${db_name}
