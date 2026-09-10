#!/bin/bash
set -e

echo "=== Installing Dependencies ==="
python3 -m pip install -r requirements.txt

echo "=== Running Migrations (optional) ==="
python3 manage.py migrate --noinput || echo "Database migration skipped during build"

echo "=== Collecting Static Files ==="
python3 manage.py collectstatic --noinput --clear

echo "=== Build Completed Successfully ==="

