"""
No-op replacement for server migration that altered ProductSpecGroup.

ProductSpecGroup is removed in 0012_product_characteristic; keeping this
migration empty preserves the graph for databases that already recorded it.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0011_productspecitem_product_inline'),
    ]

    operations = []
