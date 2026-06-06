import apps.common.file_storage
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Brand.image — DB ustuni RunSQL orqali (IF NOT EXISTS).
    Django state alohida yangilanadi, qayta ADD COLUMN qilinmaydi.
    """

    dependencies = [
        ('store_core', '0007_image_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql='ALTER TABLE "Brand" ADD COLUMN IF NOT EXISTS "image" VARCHAR(512);',
            reverse_sql='ALTER TABLE "Brand" DROP COLUMN IF EXISTS "image";',
            state_operations=[
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
            ],
        ),
    ]
