# Product spec rows editable on product page (single table)

import django.db.models.deletion
from django.db import migrations, models


def backfill_spec_item_product(apps, schema_editor):
    ProductSpecItem = apps.get_model('store_core', 'ProductSpecItem')
    ProductSpecGroup = apps.get_model('store_core', 'ProductSpecGroup')
    for item in ProductSpecItem.objects.all().iterator():
        if not item.group_id:
            continue
        group = ProductSpecGroup.objects.filter(pk=item.group_id).first()
        if not group:
            continue
        ProductSpecItem.objects.filter(pk=item.pk).update(
            product_id=group.product_id,
            group_title=group.title,
            group_sort_order=group.sort_order,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0010_product_specifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='productspecitem',
            name='group_sort_order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок группы'),
        ),
        migrations.AddField(
            model_name='productspecitem',
            name='group_title',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Например: Основные характеристики, Корпус, Камера',
                verbose_name='Группа (название)',
            ),
        ),
        migrations.AddField(
            model_name='productspecitem',
            name='product',
            field=models.ForeignKey(
                blank=True,
                db_column='productId',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='spec_items',
                to='store_core.product',
                verbose_name='Товар',
            ),
        ),
        migrations.AlterField(
            model_name='productspecitem',
            name='group',
            field=models.ForeignKey(
                blank=True,
                db_column='groupId',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='store_core.productspecgroup',
                verbose_name='Группа',
            ),
        ),
        migrations.RunPython(backfill_spec_item_product, migrations.RunPython.noop),
    ]
