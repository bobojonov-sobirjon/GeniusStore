"""Sync ProductVariantSimType rows with admin «Тип SIM (основной)» for all products."""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.store_core.variant_sim_types import sync_all_variant_sim_types


class Command(BaseCommand):
    help = (
        'Remove orphan SIM type links on all product variants. '
        'Keeps multi-SIM setups where several types have realistic prices '
        '(«Управление ценами»).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only report how many variants would be updated.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        stats = sync_all_variant_sim_types(dry_run=dry_run)

        prefix = 'Would update' if dry_run else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{prefix} {stats["synced"]} / {stats["total"]} variants '
                f'(skipped multi-SIM: {stats["skipped_multi"]}, '
                f'cleared without sim_type: {stats["cleared_no_sim"]})',
            )
        )
