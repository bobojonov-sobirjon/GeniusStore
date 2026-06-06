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

echo "==> DB: merge yozuvlari + Brand.image ustuni"
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
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Brand' AND column_name = 'image'
        """
    )
    has_column = c.fetchone() is not None

    c.execute(
        "SELECT 1 FROM django_migrations WHERE app = %s AND name = %s",
        ['store_core', '0008_brand_image'],
    )
    migration_applied = c.fetchone() is not None

    if not has_column:
        print('Brand.image ustuni yo\'q — qo\'shilmoqda...')
        c.execute('ALTER TABLE "Brand" ADD COLUMN IF NOT EXISTS "image" VARCHAR(512);')
        if not migration_applied:
            c.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                ['store_core', '0008_brand_image'],
            )
            print('0008_brand_image migratsiyasi ham belgilandi')
        else:
            print('0008_brand_image allaqachon applied edi — faqat ustun qo\'shildi')
    elif not migration_applied:
        print('Ustun bor, migratsiya yo\'q — 0008 fake qilinadi (keyingi qadam)')
    else:
        print('Brand.image va migratsiya tayyor')
PY

echo "==> Migratsiya holati (agar ustun bor, lekin 0008 applied emas bo'lsa)"
python3 manage.py migrate store_core 0008_brand_image --fake 2>/dev/null || true

echo "==> Qolgan migratsiyalar"
python3 manage.py migrate

echo "==> Tayyor"
python3 manage.py showmigrations store_core | tail -5
