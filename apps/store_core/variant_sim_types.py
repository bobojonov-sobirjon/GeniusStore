"""Keep ProductVariantSimType rows in sync with admin «Тип SIM (основной)»."""
from __future__ import annotations

from typing import Any

from django.db.models import Prefetch

from apps.store_core.models import ProductVariant, ProductVariantSimType


def _price_is_close(variant_price: float | None, link_price: float | None) -> bool:
    if variant_price is None or link_price is None:
        return False
    tolerance = max(500.0, abs(variant_price) * 0.15)
    return abs(link_price - variant_price) <= tolerance


def _links_with_realistic_prices(
    variant: ProductVariant,
    links: list[ProductVariantSimType],
) -> list[ProductVariantSimType]:
    return [l for l in links if _price_is_close(variant.price, l.price)]


def is_intentional_multi_sim(variant: ProductVariant) -> bool:
    """Several SIM types with prices near variant.price — configured in «Управление ценами»."""
    links = list(variant.sim_type_links.all())
    realistic = _links_with_realistic_prices(variant, links)
    return len({l.sim_type_id for l in realistic}) > 1


def sync_primary_sim_type_link(variant: ProductVariant) -> None:
    """
    Product edit page exposes one sim_type per variant.
    Remove orphan sim_type_links left by seed/demo data.
    """
    if not variant.pk:
        return

    if not variant.sim_type_id:
        variant.sim_type_links.all().delete()
        return

    variant.sim_type_links.exclude(sim_type_id=variant.sim_type_id).delete()
    ProductVariantSimType.objects.update_or_create(
        product_variant=variant,
        sim_type_id=variant.sim_type_id,
        defaults={'price': variant.price},
    )


def sync_all_variant_sim_types(*, dry_run: bool = False) -> dict[str, int]:
    """
    Align sim_type_links with «Тип SIM (основной)» for every variant in DB.
    Skips variants with intentional multi-SIM pricing.
    """
    stats = {
        'total': 0,
        'synced': 0,
        'skipped_multi': 0,
        'cleared_no_sim': 0,
    }
    qs = (
        ProductVariant.objects.select_related('sim_type')
        .prefetch_related(
            Prefetch(
                'sim_type_links',
                queryset=ProductVariantSimType.objects.select_related('sim_type'),
            ),
        )
        .order_by('product_id', 'id')
    )
    for variant in qs.iterator(chunk_size=200):
        stats['total'] += 1
        if is_intentional_multi_sim(variant):
            stats['skipped_multi'] += 1
            continue

        if dry_run:
            links = list(variant.sim_type_links.all())
            needs_sync = (
                not variant.sim_type_id and bool(links)
            ) or (
                variant.sim_type_id
                and (
                    len(links) != 1
                    or not links
                    or links[0].sim_type_id != variant.sim_type_id
                )
            )
            if needs_sync:
                stats['synced'] += 1
            continue

        if not variant.sim_type_id:
            deleted, _ = variant.sim_type_links.all().delete()
            if deleted:
                stats['cleared_no_sim'] += deleted
            continue

        before_count = variant.sim_type_links.count()
        before_ids = set(variant.sim_type_links.values_list('sim_type_id', flat=True))
        sync_primary_sim_type_link(variant)
        if before_count != 1 or variant.sim_type_id not in before_ids:
            stats['synced'] += 1

    return stats


def sim_type_entry_from_variant(variant: ProductVariant) -> dict[str, Any] | None:
    st = variant.sim_type
    if not st:
        return None
    link = variant.sim_type_links.filter(sim_type_id=st.id).first()
    price = variant.price if link is None else link.price
    return {
        'id': str(link.id) if link else None,
        'productVariantId': str(variant.id),
        'simTypeId': str(st.id),
        'price': price,
        'simType': {'id': str(st.id), 'name': st.name},
    }


def _link_to_dict(link: ProductVariantSimType) -> dict[str, Any]:
    st = link.sim_type
    return {
        'id': str(link.id),
        'productVariantId': str(link.product_variant_id),
        'simTypeId': str(link.sim_type_id),
        'price': link.price,
        'simType': {'id': str(st.id), 'name': st.name} if st else None,
    }


def build_variant_sim_types(variant: ProductVariant) -> list[dict[str, Any]]:
    """
    simTypes for API.

    - Several sim_type_links with prices near variant.price → multi-SIM picker.
    - Otherwise → only «Тип SIM (основной)» from admin (ignores stale seed rows).
    """
    links = list(variant.sim_type_links.all())
    if not links:
        entry = sim_type_entry_from_variant(variant)
        return [entry] if entry else []

    realistic = _links_with_realistic_prices(variant, links)
    distinct = {l.sim_type_id for l in realistic}

    if len(distinct) > 1:
        return [_link_to_dict(link) for link in realistic]

    if len(realistic) == 1:
        return [_link_to_dict(realistic[0])]

    entry = sim_type_entry_from_variant(variant)
    if entry is not None:
        return [entry]

    return [_link_to_dict(link) for link in links]
