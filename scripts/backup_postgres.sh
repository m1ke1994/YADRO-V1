#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Production .env was not found." >&2
  exit 1
fi

umask 077
mkdir -p backups

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
backup_file="backups/backup_${timestamp}.sql"
temporary_file="${backup_file}.tmp"

cleanup() {
  rm -f "$temporary_file"
}
trap cleanup EXIT INT TERM

docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  exec -T postgres \
  sh -c 'pg_dump --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  > "$temporary_file"

if [ ! -s "$temporary_file" ]; then
  echo "PostgreSQL backup is empty. Deployment must not continue." >&2
  exit 1
fi

mv "$temporary_file" "$backup_file"
trap - EXIT INT TERM

echo "PostgreSQL backup created: $backup_file"
ls -lh "$backup_file"
