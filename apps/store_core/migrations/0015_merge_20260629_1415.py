"""Merge ProductCharacteristic branch and legacy ProductSpecGroup branch."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0013_merge_20260625_0853'),
        ('store_core', '0014_drop_variant_source_column'),
    ]

    operations = []
