"""Ensure variant_source column is removed from ProductCharacteristic (production fix)."""

from django.db import migrations


class Migration(migrations.Migration):
    """
    0013 may not have been applied on production while code without variant_source
    was deployed — inserts then fail with NOT NULL on variant_source.
  """

    dependencies = [
        ('store_core', '0013_remove_productcharacteristic_variant_source'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "ProductCharacteristic" DROP COLUMN IF EXISTS "variant_source";',
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
