#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set=app_password="$DB_APP_PASSWORD" <<'EOSQL'
CREATE ROLE restaurant_app LOGIN PASSWORD :'app_password';
EOSQL
