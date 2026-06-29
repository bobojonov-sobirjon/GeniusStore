"""
No-op replacement for server merge migration.

The original 0013_merge altered ProductSpecGroup, but 0012 removed that model.
Keeping empty operations lets both migration branches merge safely.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0011_productspecitem_product_inline'),
    ]

    operations = []
