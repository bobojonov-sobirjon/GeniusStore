from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0012_product_characteristic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productcharacteristic',
            name='variant_source',
        ),
    ]
