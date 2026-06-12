#!/usr/bin/env bash
# Run on production after deploy. Admin CSS breaks when STATIC_URL is relative.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== 1) Git commit (expect: fix STATIC_URL) ==="
git log -1 --oneline

echo ""
echo "=== 2) STATIC_URL in settings.py ==="
grep '^STATIC_URL' config/settings.py

echo ""
echo "=== 3) Django runtime STATIC_URL ==="
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); import django; django.setup(); from django.conf import settings; print('STATIC_URL =', repr(settings.STATIC_URL))"

echo ""
echo "=== 4) staticfiles on disk ==="
test -f staticfiles/vendor/adminlte/css/adminlte.min.css && echo "OK: adminlte.min.css exists" || echo "MISSING: run collectstatic"

echo ""
echo "=== 5) HTTP /static/ (must be CSS, not HTML) ==="
CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://admin.geniusstorerf.ru/static/vendor/adminlte/css/adminlte.min.css")
echo "GET /static/vendor/adminlte/css/adminlte.min.css -> HTTP $CODE"

echo ""
echo "=== 6) WRONG path (if this returns 200 HTML, STATIC_URL fix NOT applied) ==="
BODY=$(curl -s "https://admin.geniusstorerf.ru/admin/store_core/storeuser/static/vendor/adminlte/css/adminlte.min.css" | head -c 80)
echo "$BODY"
if echo "$BODY" | grep -qi 'войти\|login'; then
    echo "FAIL: admin still uses relative static/ paths. Run: git pull && sudo systemctl restart geniusstore"
    exit 1
fi

echo ""
echo "=== OK ==="
