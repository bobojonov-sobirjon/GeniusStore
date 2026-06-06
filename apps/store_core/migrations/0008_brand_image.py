import apps.common.file_storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0007_image_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "Brand" ADD COLUMN IF NOT EXISTS "image" VARCHAR(512);',
            reverse_sql='ALTER TABLE "Brand" DROP COLUMN IF EXISTS "image";',
        ),
        migrations.AddField(
            model_name='brand',
            name='image',
            field=models.ImageField(
                blank=True,
                max_length=512,
                null=True,
                upload_to=apps.common.file_storage.image_upload_to,
                verbose_name='Изображение',
            ),
        ),
    ]
