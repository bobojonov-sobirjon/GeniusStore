"""ProductVariant.memory is optional (nullable memoryId)."""

import django.db.models.deletion
from django.db import migrations, models


def apply_nullable_memory(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "ProductVariant" ALTER COLUMN "memoryId" DROP NOT NULL;')


def reverse_nullable_memory(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE "ProductVariant"
            SET "memoryId" = (
                SELECT id FROM "Memory" ORDER BY id LIMIT 1
            )
            WHERE "memoryId" IS NULL;
            """
        )
        cursor.execute('ALTER TABLE "ProductVariant" ALTER COLUMN "memoryId" SET NOT NULL;')


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0018_cascade_delete_relations'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='productvariant',
                    name='memory',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='memoryId',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='variants',
                        to='store_core.memory',
                        verbose_name='Память',
                    ),
                ),
            ],
            database_operations=[
                migrations.RunPython(apply_nullable_memory, reverse_nullable_memory),
            ],
        ),
    ]
