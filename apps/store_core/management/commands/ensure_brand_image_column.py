"""Ensure Brand.image column exists (safe for production after --fake migrate)."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Add Brand.image column if missing in PostgreSQL'

    def handle(self, *args, **options):
        with connection.cursor() as c:
            c.execute(
                """
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'Brand' AND column_name = 'image'
                """
            )
            if c.fetchone():
                self.stdout.write(self.style.SUCCESS('Brand.image ustuni allaqachon mavjud'))
                return
            c.execute('ALTER TABLE "Brand" ADD COLUMN "image" VARCHAR(512);')
        self.stdout.write(self.style.SUCCESS('Brand.image ustuni qo\'shildi'))
