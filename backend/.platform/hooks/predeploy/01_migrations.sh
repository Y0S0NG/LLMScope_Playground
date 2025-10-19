#!/bin/bash
# Run database migrations before deployment

set -e

echo "Running Alembic migrations..."
source /var/app/venv/*/bin/activate
cd /var/app/staging

alembic upgrade head

echo "Migrations completed successfully"
