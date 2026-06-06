import apps.common.file_storage
from django.db import migrations, models


def normalize_review_thumbnails(apps, schema_editor):
    from apps.common.file_storage import normalize_stored_image_path

    Review = apps.get_model('storefront', 'Review')
    for review in Review.objects.all():
        value = review.thumbnail
        if not value:
            continue
        normalized = normalize_stored_image_path(str(value))
        if normalized and normalized != value:
            Review.objects.filter(pk=review.pk).update(thumbnail=normalized)


class Migration(migrations.Migration):

    dependencies = [
        ('storefront', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(normalize_review_thumbnails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='review',
            name='thumbnail',
            field=models.ImageField(
                blank=True,
                max_length=512,
                upload_to=apps.common.file_storage.image_upload_to,
                verbose_name='Файл превью',
            ),
        ),
    ]
