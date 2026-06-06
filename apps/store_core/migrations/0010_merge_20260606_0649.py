# Merge production branches: 0006_merge + 0009 (brand image path).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0006_merge_20260603_0209'),
        ('store_core', '0009_merge_20260606_0647'),
    ]

    operations = []
