#!/usr/bin/env bash
set -euo pipefail

if ! psql --username "$POSTGRES_USER" --dbname postgres --tuples-only --no-align \
  --command "SELECT 1 FROM pg_database WHERE datname = 'tracker_backup'" | grep -qx '1'; then
  psql --username "$POSTGRES_USER" --dbname postgres \
    --command 'CREATE DATABASE tracker_backup'
fi
