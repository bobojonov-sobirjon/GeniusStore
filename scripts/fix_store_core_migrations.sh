#!/bin/bash
# Serverda migratsiya aralashgan bo'lsa — bitta buyruq bilan tiklash.
# Ishlatish: cd /var/www/GeniusStore && bash scripts/fix_store_core_migrations.sh

set -e
cd "$(dirname "$0")/.."
source env/bin/activate

echo "==> Git: server kodini GitHub bilan bir xil qilish"
git fetch origin
git reset --hard origin/main
git clean -fd apps/store_core/migrations/

echo "==> Migratsiya fayllari:"
ls -1 apps/store_core/migrations/*.py

echo "==> DB: eski merge yozuvlarini tozalash (agar bor bo'lsa)"
python3 manage.py shell <<'PY'
from django.db import connection

ORPHANS = (
    '0005_alter_banner_created_at',
    '0006_merge_20260603_0209',
    '0008_merge_0006_merge_20260603_0209_0007_image_fields',
    '0009_merge_20260606_0647',
    '0010_merge_20260606_0649',
    '0010_merge_20260606_0651',
)

with connection.cursor() as c:
    for name in ORPHANS:
        c.execute(
            "DELETE FROM django_migrations WHERE app = %s AND name = %s",
            ['store_core', name],
        )
    c.execute(
        "SELECT 1 FROM django_migrations WHERE app = %s AND name = %s",
        ['store_core', '0008_brand_image'],
    )
    if c.fetchone():
        print('0008_brand_image allaqachon applied — fake kerak emas')
    else:
        print('0008_brand_image hali applied emas — keyin migrate ishlaydi')
PY

echo "==> Brand.image ustuni mavjud bo'lsa, 0008 ni fake qilish"
python3 manage.py migrate store_core 0008_brand_image --fake 2>/dev/null || true

echo "==> Qolgan migratsiyalar"
python3 manage.py migrate

echo "==> Tayyor"
python3 manage.py showmigrations store_core | tail -5
