"""Cascade delete for products/blog: DB FK constraints aligned with Django models."""

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


def _table_exists(cursor, table: str) -> bool:
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        )
        """,
        [table],
    )
    return bool(cursor.fetchone()[0])


def _set_fk(cursor, table: str, column: str, ref_table: str, ref_column: str, on_delete: str) -> None:
    _drop_fk(cursor, table, column)
    constraint = f'{table}_{column}_fkey'
    cursor.execute(
        f"""
        ALTER TABLE "{table}"
        ADD CONSTRAINT "{constraint}"
        FOREIGN KEY ("{column}") REFERENCES "{ref_table}"("{ref_column}")
        ON DELETE {on_delete} ON UPDATE CASCADE;
        """
    )


def apply_cascade_fks(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        _set_fk(cursor, 'BlogSteps', 'blogId', 'Blog', 'id', 'CASCADE')

        _set_fk(cursor, 'ProductVariant', 'productId', 'Product', 'id', 'CASCADE')
        _set_fk(cursor, 'ProductVariantSimType', 'productVariantId', 'ProductVariant', 'id', 'CASCADE')

        cursor.execute('ALTER TABLE "OrderItem" ALTER COLUMN "productVariantId" DROP NOT NULL;')
        _set_fk(cursor, 'OrderItem', 'productVariantId', 'ProductVariant', 'id', 'SET NULL')

        if _table_exists(cursor, 'ProductImage'):
            _set_fk(cursor, 'ProductImage', 'productId', 'Product', 'id', 'CASCADE')

        if _table_exists(cursor, 'ProductCharacteristic'):
            _set_fk(cursor, 'ProductCharacteristic', 'productId', 'Product', 'id', 'CASCADE')


def reverse_cascade_fks(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        _set_fk(cursor, 'BlogSteps', 'blogId', 'Blog', 'id', 'RESTRICT')
        _set_fk(cursor, 'ProductVariant', 'productId', 'Product', 'id', 'RESTRICT')
        _set_fk(cursor, 'ProductVariantSimType', 'productVariantId', 'ProductVariant', 'id', 'CASCADE')
        _set_fk(cursor, 'OrderItem', 'productVariantId', 'ProductVariant', 'id', 'RESTRICT')


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0017_product_cascade_delete'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='blogsteps',
                    name='blog',
                    field=models.ForeignKey(
                        db_column='blogId',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='blogSteps',
                        to='store_core.blog',
                        verbose_name='Статья',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(apply_cascade_fks, reverse_cascade_fks),
            ],
        ),
    ]
