# Generated manually — order contact fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0005_orderitem_storeorder_delivery_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeorder',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='storeorder',
            name='full_name',
            field=models.CharField(blank=True, db_column='fullName', default='', max_length=255, verbose_name='ФИО'),
        ),
        migrations.AddField(
            model_name='storeorder',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=32, verbose_name='Телефон'),
        ),
    ]
