# Merge parallel 0008 branches (brand image + banner created_at path).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0008_brand_image'),
        ('store_core', '0008_merge_0006_merge_20260603_0209_0007_image_fields'),
    ]

    operations = []
