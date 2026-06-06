# Parallel branch from 0007 (created on server via makemigrations --merge).
# Banner created_at is already fixed in 0007_image_fields — this branch is a no-op.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0007_image_fields'),
    ]

    operations = []
