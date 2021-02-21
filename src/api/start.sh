#!/bin/sh
# start.sh

set -e
  
until pg_isready -h db; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up - executing commands"

python importer.py
flask run