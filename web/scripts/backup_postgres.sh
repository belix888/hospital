#!/usr/bin/env sh
set -eu

# Usage:
#   DATABASE_URL=postgres://user:pass@host:5432/db ./scripts/backup_postgres.sh
#
# Requires: pg_dump available (run inside postgres container or install client tools).

ts="$(date +%Y%m%d-%H%M%S)"
out="backup-${ts}.sql.gz"

echo "Creating ${out}"
pg_dump "${DATABASE_URL}" | gzip > "${out}"
echo "Done"

