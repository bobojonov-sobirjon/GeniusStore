"""Cascade delete Product -> ProductVariant; preserve orders when variant removed."""

import django.db.models.deletion
from django.db import migrations, models


def _drop_fk(cursor, table: str, column: str) -> None:
    cursor.execute(
        """
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_attribute att ON att.attrelid = con.conrelid
            AND att.attnum = ANY(con.conkey)
        WHERE rel.relname = %s
          AND att.attname = %s
          AND con.contype = 'f'
        """,
        [table, column],
    )
    for (conname,) in cursor.fetchall():
        cursor.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT "{conname}"')


def apply_cascade_fks(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        _drop_fk(cursor, 'ProductVariant', 'productId')
        cursor.execute(
            """
            ALTER TABLE "ProductVariant"
            ADD CONSTRAINT "ProductVariant_productId_fkey"
            FOREIGN KEY ("productId") REFERENCES "Product"("id")
            ON DELETE CASCADE ON UPDATE CASCADE;
            """
        )

        cursor.execute(
            'ALTER TABLE "OrderItem" ALTER COLUMN "productVariantId" DROP NOT NULL;'
        )
        _drop_fk(cursor, 'OrderItem', 'productVariantId')
        cursor.execute(
            """
            ALTER TABLE "OrderItem"
            ADD CONSTRAINT "OrderItem_productVariantId_fkey"
            FOREIGN KEY ("productVariantId") REFERENCES "ProductVariant"("id")
            ON DELETE SET NULL ON UPDATE CASCADE;
            """
        )


def reverse_cascade_fks(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        _drop_fk(cursor, 'ProductVariant', 'productId')
        cursor.execute(
            """
            ALTER TABLE "ProductVariant"
            ADD CONSTRAINT "ProductVariant_productId_fkey"
            FOREIGN KEY ("productId") REFERENCES "Product"("id")
            ON DELETE RESTRICT ON UPDATE CASCADE;
            """
        )

        _drop_fk(cursor, 'OrderItem', 'productVariantId')
        cursor.execute(
            """
            ALTER TABLE "OrderItem"
            ADD CONSTRAINT "OrderItem_productVariantId_fkey"
            FOREIGN KEY ("productVariantId") REFERENCES "ProductVariant"("id")
            ON DELETE RESTRICT ON UPDATE CASCADE;
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0016_merge_20260629_1417'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='productvariant',
                    name='product',
                    field=models.ForeignKey(
                        db_column='productId',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='variants',
                        to='store_core.product',
                        verbose_name='Товар',
                    ),
                ),
                migrations.AlterField(
                    model_name='orderitem',
                    name='product_variant',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='productVariantId',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='order_items',
                        to='store_core.productvariant',
                        verbose_name='Вариант товара',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(apply_cascade_fks, reverse_cascade_fks),
            ],
        ),
    ]
