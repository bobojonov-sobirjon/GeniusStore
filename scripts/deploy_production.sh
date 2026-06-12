#!/usr/bin/env bash
# Deploy latest code + static files on production server.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> git pull"
git pull origin main

echo "==> collectstatic"
python manage.py collectstatic --noinput

echo "==> restart app"
if systemctl is-active --quiet geniusstore 2>/dev/null; then
    sudo systemctl restart geniusstore
elif systemctl is-active --quiet gunicorn 2>/dev/null; then
    sudo systemctl restart gunicorn
else
    echo "Warning: no geniusstore/gunicorn service found — restart your WSGI process manually."
fi

echo "==> verify static (must return CSS, not HTML login page)"
curl -sI "http://127.0.0.1/static/vendor/adminlte/css/adminlte.min.css" | head -n 1 || true

echo "==> done"
echo "Hard-refresh admin in browser: Ctrl+F5"
