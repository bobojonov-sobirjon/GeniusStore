"""Merge legacy ProductSpecGroup branch with ProductCharacteristic branch."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0012_alter_productspecgroup_options_and_more'),
        ('store_core', '0015_merge_20260629_1415'),
    ]

    operations = []
