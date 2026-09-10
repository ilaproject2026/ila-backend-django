#!/bin/bash
set -e

export PIP_BREAK_SYSTEM_PACKAGES=1

echo "=== Installing Dependencies ==="
python3 -m pip install -r requirements.txt --break-system-packages

echo "=== Running Migrations (optional) ==="
python3 manage.py migrate --noinput || echo "Database migration skipped during build"

echo "=== Collecting Static Files ==="
python3 manage.py collectstatic --noinput --clear

echo "=== Build Completed Successfully ==="


