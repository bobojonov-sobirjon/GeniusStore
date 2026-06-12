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
echo "=== 5) Bootstrap/Bootswatch versions must match (BS5, not BS4) ==="
BS_VER=$(curl -s "https://admin.geniusstorerf.ru/static/vendor/bootswatch/flatly/bootstrap.min.css" | head -c 120)
echo "bootswatch header: $BS_VER"
if echo "$BS_VER" | grep -q 'Bootswatch v4'; then
    echo "FAIL: still serving Bootswatch v4 — run: pip install -r requirements.txt && python manage.py collectstatic --clear --noinput"
    exit 1
fi
if ! echo "$BS_VER" | grep -q 'Bootswatch v5'; then
    echo "WARN: expected Bootswatch v5.x"
fi

echo ""
echo "=== 6) HTTP /static/ (must be CSS, not HTML) ==="
CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://admin.geniusstorerf.ru/static/vendor/adminlte/css/adminlte.min.css")
echo "GET /static/vendor/adminlte/css/adminlte.min.css -> HTTP $CODE"

echo ""
echo "=== 7) Admin HTML must use /static/ (absolute), not static/ (relative) ==="
HTML=$(curl -s "https://admin.geniusstorerf.ru/admin/login/")
if echo "$HTML" | grep -q 'href="/static/'; then
    echo "OK: login page links to /static/"
else
    echo "FAIL: login page missing href=\"/static/\" — restart gunicorn/daphne"
    exit 1
fi
if echo "$HTML" | grep -q 'href="static/'; then
    echo "FAIL: login page still has relative href=\"static/\""
    exit 1
fi

echo ""
echo "=== 8) WRONG nested path must NOT return login HTML ==="
BODY=$(curl -s "https://admin.geniusstorerf.ru/admin/store_core/storeuser/static/vendor/adminlte/css/adminlte.min.css" | head -c 80)
if echo "$BODY" | grep -qi 'войти\|login'; then
    echo "FAIL: nested /admin/.../static/ still hits Django HTML"
    exit 1
fi
echo "OK"

echo ""
echo "If verify OK but browser still broken: Ctrl+Shift+R or Incognito (old HTML cache)."
echo ""
echo "=== OK ==="
