#!/usr/bin/env bash
# Deploy latest code + static files on production server.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> git pull"
git pull origin main

echo "==> STATIC_URL (must be /static/)"
grep '^STATIC_URL' config/settings.py

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

echo "==> verify"
bash scripts/verify_admin_static.sh || true

echo "==> done"
echo "Hard-refresh admin in browser: Ctrl+F5"
