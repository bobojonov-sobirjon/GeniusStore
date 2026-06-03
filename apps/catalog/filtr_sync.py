from __future__ import annotations

from typing import Any

from django.db.models import Count, Prefetch, Q

from apps.catalog.serialization import product_to_dict
from apps.store_core.models import (
    Brand,
    Category,
    Color,
    Condition,
    Memory,
    Product,
    ProductModel,
    ProductVariant,
    ProductVariantSimType,
    SimType,
)


def get_brands_and_models_by_category(category_id: int) -> list[dict]:
    brands = (
        Brand.objects.filter(products__category_id=category_id, products__product_model_id__isnull=False)
        .distinct()
        .prefetch_related(
            Prefetch(
                'products',
                queryset=Product.objects.filter(category_id=category_id, product_model_id__isnull=False).select_related(
                    'product_model'
                ),
            )
        )
    )
    result = []
    for b in brands:
        models_map: dict[int, dict] = {}
        for p in b.products.all():
            if p.product_model_id and p.product_model:
                models_map[p.product_model.id] = {'id': p.product_model.id, 'name': p.product_model.name}
        if models_map:
            result.append({'brand': b.name, 'id': b.id, 'models': list(models_map.values())})
    return result


def get_best_offers(limit: int = 8) -> dict[str, list]:
    used = Condition.objects.filter(name='Б/у').first()
    used_id = used.id if used else None
    vqs = ProductVariant.objects.select_related('memory')
    base = Product.objects.select_related('brand', 'product_model', 'category', 'condition').prefetch_related(
        Prefetch('variants', queryset=vqs)
    )

    def pack(qs):
        return [product_to_dict(p) for p in qs[:limit]]

    sales = pack(base.order_by('-created_at'))
    hits = pack(base.filter(is_hit=True).order_by('-created_at'))
    news = pack(base.filter(is_new=True).order_by('-created_at'))
    used_list = pack(base.filter(condition_id=used_id).order_by('-created_at')) if used_id else []
    return {'sales': sales, 'hits': hits, 'news': news, 'used': used_list}


def get_filter_data(slug: str, model_id: int | None, brand_id: int | None) -> dict[str, Any]:
    category = Category.objects.filter(slug=slug).values('id', 'name').first()
    if not category:
        return {
            'category': [],
            'brand': [],
            'condition': [],
            'model': [],
            'simType': [],
            'memory': [],
            'color': [],
            'availableCount': 0,
        }
    cid = category['id']
    scoped_brand_ids = None
    if brand_id:
        scoped_brand_ids = [brand_id]
    elif model_id:
        scoped_brand_ids = list(
            Product.objects.filter(category_id=cid, product_model_id=model_id)
            .values_list('brand_id', flat=True)
            .distinct()
        )
        if not scoped_brand_ids:
            scoped_brand_ids = None

    prod_q = Product.objects.filter(category_id=cid)
    if scoped_brand_ids:
        prod_q = prod_q.filter(brand_id__in=scoped_brand_ids)
    available_count = prod_q.filter(is_available=True).count()

    categories = []
    for c in Category.objects.annotate(count=Count('products')).order_by('created_at'):
        categories.append({'id': c.id, 'name': c.name, 'icon': c.icon, 'slug': c.slug, 'count': c.count})

    brand_filter = Q(products__category_id=cid)
    brands = []
    for b in Brand.objects.filter(brand_filter).distinct().order_by('created_at'):
        cnt = Product.objects.filter(brand=b, category_id=cid).count()
        brands.append({'id': b.id, 'name': b.name, 'createdAt': b.created_at, 'count': cnt})

    cond_filter = Q(products__category_id=cid)
    if scoped_brand_ids:
        cond_filter &= Q(products__brand_id__in=scoped_brand_ids)
    conditions = []
    for c in Condition.objects.filter(cond_filter).distinct().order_by('created_at'):
        pq = Product.objects.filter(category_id=cid, condition=c)
        if scoped_brand_ids:
            pq = pq.filter(brand_id__in=scoped_brand_ids)
        conditions.append(
            {'id': str(c.id), 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at, 'count': pq.count()}
        )

    model_filter = Q(products__category_id=cid)
    if scoped_brand_ids:
        model_filter &= Q(products__brand_id__in=scoped_brand_ids)
    models = []
    for m in ProductModel.objects.filter(model_filter).distinct().order_by('created_at'):
        pq = Product.objects.filter(category_id=cid, product_model=m)
        if scoped_brand_ids:
            pq = pq.filter(brand_id__in=scoped_brand_ids)
        models.append({'id': m.id, 'name': m.name, 'createdAt': m.created_at, 'count': pq.count()})

    sim_types = []
    for s in SimType.objects.annotate(count=Count('variants_single')).order_by('id'):
        sim_types.append({'id': str(s.id), 'name': s.name, 'count': s.count})

    memories = []
    mem_qs = Memory.objects.filter(variants__product__category_id=cid).distinct().order_by('name')
    if scoped_brand_ids:
        mem_qs = mem_qs.filter(variants__product__brand_id__in=scoped_brand_ids)
    for mem in mem_qs:
        vq = ProductVariant.objects.filter(memory=mem, product__category_id=cid)
        if scoped_brand_ids:
            vq = vq.filter(product__brand_id__in=scoped_brand_ids)
        memories.append({'id': mem.id, 'name': mem.name, 'createdAt': mem.created_at, 'count': vq.count()})

    color_rows = []
    col_qs = Color.objects.filter(variants__product__category_id=cid).distinct().order_by('name')
    if scoped_brand_ids:
        col_qs = col_qs.filter(variants__product__brand_id__in=scoped_brand_ids)
    for col in col_qs:
        vq = ProductVariant.objects.filter(color=col, product__category_id=cid)
        if scoped_brand_ids:
            vq = vq.filter(product__brand_id__in=scoped_brand_ids)
        color_rows.append({'id': col.id, 'name': col.name, 'hex': col.hex, 'count': vq.count()})

    return {
        'category': categories,
        'brand': brands,
        'condition': conditions,
        'model': models,
        'simType': sim_types,
        'memory': memories,
        'color': color_rows,
        'availableCount': available_count,
    }


def _truthy_local(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).lower() in ('true', '1', 'yes')


def _variant_matches_sim_types(v: ProductVariant, sim_types: list[Any]) -> bool:
    if not sim_types:
        return True
    has_null = any(t is None or t == 'null' or t == '' or t is False for t in sim_types)
    non_null = [str(t) for t in sim_types if t not in (None, 'null', '', 'undefined') and t is not False]
    singles = [str(v.sim_type_id)] if v.sim_type_id else []
    m2m = [str(l.sim_type_id) for l in v.sim_type_links.all()]
    all_ids = set(singles + m2m)
    if has_null and not non_null:
        return v.sim_type_id is None and not m2m
    if has_null and non_null:
        return any(i in non_null for i in all_ids) or (v.sim_type_id is None and not m2m)
    if non_null:
        return any(i in non_null for i in all_ids)
    return True


def _body_list(body: dict, *keys: str) -> list[Any]:
    for key in keys:
        val = body.get(key)
        if val is None or val == '':
            continue
        if isinstance(val, list):
            return val
        return [val]
    return []


def filter_products(body: dict) -> list[dict]:
    slug = body.get('slug')
    brands = _body_list(body, 'brands', 'brandIds', 'brandId')
    conditions = _body_list(body, 'conditions', 'conditionIds', 'conditionId')
    models = _body_list(body, 'models', 'modelIds', 'modelId')
    colors = _body_list(body, 'colors', 'colorIds', 'colorId')
    memories = _body_list(body, 'memories', 'memoryIds', 'memoryId', 'memory')
    min_price = body.get('minPrice')
    max_price = body.get('maxPrice')
    in_stock = body.get('inStock')
    category_id = body.get('categoryId')
    sim_types = _body_list(body, 'simTypes', 'simTypeIds', 'simTypeId')
    is_bt = body.get('isBt')
    is_all = body.get('isAll')

    pq = Product.objects.select_related('brand', 'category', 'condition', 'product_model').prefetch_related(
        Prefetch(
            'variants',
            queryset=ProductVariant.objects.select_related('memory', 'color', 'sim_type').prefetch_related(
                Prefetch('sim_type_links', queryset=ProductVariantSimType.objects.select_related('sim_type'))
            ),
        )
    )

    q = Q()
    if is_bt is not None:
        q &= Q(is_bt=_truthy_local(is_bt))
    if is_all is not True:
        if slug:
            q &= Q(category__slug=slug)
        elif category_id and int(category_id) != 0:
            q &= Q(category_id=int(category_id))
        if brands:
            q &= Q(brand_id__in=[int(x) for x in brands])
        if conditions:
            q &= Q(condition_id__in=list(conditions))
        if models:
            q &= Q(product_model_id__in=[int(x) for x in models])

    products = list(pq.filter(q).order_by('-created_at'))

    def variant_ok(v: ProductVariant) -> bool:
        if is_all is not True and memories and v.memory_id not in [int(x) for x in memories]:
            return False
        if is_all is not True and colors and v.color_id not in [int(x) for x in colors]:
            return False
        if is_all is not True and min_price is not None and max_price is not None:
            if not (float(min_price) <= v.price <= float(max_price)):
                return False
        elif is_all is not True and min_price is not None:
            if v.price < float(min_price):
                return False
        elif is_all is not True and max_price is not None:
            if v.price > float(max_price):
                return False
        if in_stock and is_all is not True and not v.is_available:
            return False
        if sim_types and is_all is not True and not _variant_matches_sim_types(v, sim_types):
            return False
        return True

    variant_where_used = bool(
        (memories and is_all is not True)
        or (colors and is_all is not True)
        or (min_price is not None and is_all is not True)
        or (max_price is not None and is_all is not True)
        or (in_stock and is_all is not True)
        or (sim_types and is_all is not True)
    )

    rows: list[tuple[Product, list[ProductVariant], float | None]] = []
    for p in products:
        vars_all = list(p.variants.all())
        vars_f = [v for v in vars_all if variant_ok(v)] if variant_where_used else vars_all
        if variant_where_used and not vars_f:
            continue
        prices = []
        for v in vars_f:
            prices.append(v.price)
            for l in v.sim_type_links.all():
                if l.price is not None:
                    prices.append(float(l.price))
        min_p = min(prices) if prices else None
        rows.append((p, vars_f, min_p))

    def sort_key(item: tuple[Product, list[ProductVariant], float | None]):
        p, _, min_p = item
        pm = p.product_model
        model_date = pm.created_at.timestamp() if pm else 0.0
        created = p.created_at.timestamp() if p.created_at else 0.0
        return (-model_date, min_p if min_p is not None else float('inf'), -created)

    rows.sort(key=sort_key)
    return [
        {**product_to_dict(p, vf), 'minPrice': min_p}
        for p, vf, min_p in rows
    ]


def is_has_product(slug: str) -> bool:
    return Product.objects.filter(slug=slug).exists()


def clean_all_sim_type_id_products() -> str:
    return 'OK'


def filtr_by_variant_sim_type_products(simtype_id: str) -> dict:
    qs = Product.objects.filter(variants__sim_type_id=simtype_id).distinct()
    return {'data': list(qs.values())}
