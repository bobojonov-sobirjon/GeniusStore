from __future__ import annotations

from random import choice, randint, uniform

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts import services_sync as acc
from apps.store_core.models import (
    Banner,
    Blog,
    BlogCategory,
    BlogSteps,
    Brand,
    Category,
    Color,
    Condition,
    Info,
    Memory,
    Product,
    ProductImage,
    ProductModel,
    ProductVariant,
    ProductVariantSimType,
    Service,
    ServiceBrand,
    ServiceModel,
    SimType,
    StoreAdmin,
    StoreOrder,
    StoreUser,
)
from apps.storefront.models import CartItem, Favorite, Review, SiteSettings


class Command(BaseCommand):
    help = "Fill all models with fake demo data (Whale Store style)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-superuser',
            action='store_true',
            help='Create Django admin superuser (admin / admin123)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['with_superuser']:
            self._seed_django_superuser()

        self._seed_users_admins()
        categories = self._seed_categories()
        brands = self._seed_brands()
        models = self._seed_product_models()
        conditions = self._seed_conditions()
        memories = self._seed_memories()
        colors = self._seed_colors()
        sim_types = self._seed_sim_types()
        products = self._seed_products(categories, brands, models, conditions)
        variants = self._seed_variants(products, memories, colors, sim_types)
        self._seed_product_images(products, variants)
        from apps.store_core.seed_characteristics import seed_product_characteristics
        seed_product_characteristics(products)
        self._seed_orders(variants)
        self._seed_blog()
        self._seed_repair()
        self._seed_banners_and_info()
        self._seed_storefront(variants)
        self.stdout.write(self.style.SUCCESS('Fake data seeded successfully.'))
        self.stdout.write('Demo product with color galleries: GET /api/product/slug/apple-iphone-13')
        self.stdout.write('Django admin: admin / admin123  (--with-superuser)')
        self.stdout.write('Store users: demo1@geniusstore.local / 12345678')

    def _seed_django_superuser(self) -> None:
        User = get_user_model()
        if User.objects.filter(username='admin').exists():
            self.stdout.write('Django superuser "admin" already exists.')
            return
        User.objects.create_superuser(
            username='admin',
            email='admin@geniusstore.local',
            password='admin123',
        )
        self.stdout.write(self.style.SUCCESS('Created Django superuser: admin / admin123'))

    def _seed_users_admins(self) -> None:
        admins = [
            ('superadmin', 'admin123'),
            ('manager', 'manager123'),
        ]
        for username, password in admins:
            if not StoreAdmin.objects.filter(username=username).exists():
                StoreAdmin.objects.create(username=username, password=acc.hash_admin_password(password))

        users = [
            {'email': 'demo1@geniusstore.local', 'phone': '+79990000001', 'first_name': 'Aziz', 'last_name': 'Karimov'},
            {'email': 'demo2@geniusstore.local', 'phone': '+79990000002', 'first_name': 'Nodira', 'last_name': 'Rustamova'},
            {'email': 'demo3@geniusstore.local', 'phone': '+79990000003', 'first_name': 'Sardor', 'last_name': 'Yunusov'},
            {'email': 'ivan.petrov@mail.ru', 'phone': '+79991234567', 'first_name': 'Иван', 'last_name': 'Петров'},
            {'email': 'maria.sokolova@gmail.com', 'phone': '+79997654321', 'first_name': 'Мария', 'last_name': 'Соколова'},
            {'email': 'alex.kuznetsov@yandex.ru', 'phone': '+79995556677', 'first_name': 'Алексей', 'last_name': 'Кузнецов'},
            {'email': 'elena.volkova@mail.ru', 'phone': '+79998887766', 'first_name': 'Елена', 'last_name': 'Волкова'},
            {'email': 'dmitry.orlov@gmail.com', 'phone': '+79991112233', 'first_name': 'Дмитрий', 'last_name': 'Орлов'},
        ]
        for row in users:
            StoreUser.objects.get_or_create(
                email=row['email'],
                defaults={
                    'phone': row['phone'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'password': acc.hash_user_password('12345678'),
                    'avatar': 'uploads/image/user-default.png',
                },
            )

    def _seed_categories(self) -> list[Category]:
        rows = [
            ('Смартфоны', 'smartfony'),
            ('Планшеты', 'planshety'),
            ('Ноутбуки', 'noutbuki'),
            ('Наушники', 'naushniki'),
            ('Смарт-часы', 'smart-chasy'),
            ('Камеры', 'kamery'),
            ('Игровые консоли', 'igrovye-konsoli'),
            ('Аксессуары', 'aksessuary'),
            ('Б/у техника', 'bu-tekhnika'),
            ('Пылесосы', 'pylesosy'),
        ]
        out = []
        for name, slug in rows:
            obj, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'icon': ''},
            )
            out.append(obj)
        return out

    def _seed_brands(self) -> list[Brand]:
        names = [
            'Apple', 'Samsung', 'Dyson', 'Sony', 'Valve', 'Yandex',
            'Canon', 'FUJIFILM', 'GoPro', 'Marshall', 'Google', 'Xiaomi',
        ]
        slug_map = {
            'Apple': 'apple',
            'Samsung': 'samsung',
            'Dyson': 'dyson',
            'Sony': 'sony',
            'Valve': 'valve',
            'Yandex': 'yandex',
            'Canon': 'canon',
            'FUJIFILM': 'fujifilm',
            'GoPro': 'gopro',
            'Marshall': 'marshall',
            'Google': 'google',
            'Xiaomi': 'xiaomi',
        }
        out = []
        for name in names:
            obj, created = Brand.objects.get_or_create(name=name)
            if created or not obj.image:
                slug = slug_map.get(name, name.lower().replace(' ', '-'))
                obj.image = f'uploads/image/brand-{slug}.png'
                obj.save(update_fields=['image'])
            out.append(obj)
        return out

    def _seed_product_models(self) -> list[ProductModel]:
        names = [
            'Apple iPhone 17', 'Apple iPhone 17 Pro', 'Apple iPhone 17 Pro Max',
            'Apple iPhone 16 Pro', 'Apple iPhone 16e', 'Apple iPhone 13 Pro', 'Apple iPhone 13',
            'Samsung Galaxy S26 Ultra', 'Samsung Galaxy Z Fold7', 'Samsung Galaxy Z Fold 6',
            'Google Pixel 10 Pro XL', 'Google Pixel 9 Pro',
            'Xiaomi Redmi Note 14 Pro', 'Sony WH-1000XM6', 'Dyson V15 Detect',
            'Valve Steam Deck OLED', 'GoPro Hero 13', 'Canon EOS R6 Mark II',
        ]
        out = []
        for name in names:
            obj, _ = ProductModel.objects.get_or_create(name=name)
            out.append(obj)
        return out

    def _seed_conditions(self) -> list[Condition]:
        out = []
        for name in ['Новый', 'Уценка', 'Б/у']:
            obj, _ = Condition.objects.get_or_create(name=name)
            out.append(obj)
        return out

    def _seed_memories(self) -> list[Memory]:
        out = []
        for name in ['128 GB', '256 GB', '512 GB', '1 TB', '2 TB']:
            obj, _ = Memory.objects.get_or_create(name=name)
            out.append(obj)
        return out

    def _seed_colors(self) -> list[Color]:
        rows = [
            ('Green', '#34C759'),
            ('Blue', '#007AFF'),
            ('Starlight', '#F5F0E8'),
            ('Midnight', '#1C1C1E'),
            ('Silver', '#C0C0C0'),
            ('Orange', '#F97316'),
            ('Cosmic Orange', '#EA580C'),
            ('Черный', '#0F0F0F'),
            ('Белый', '#F7F7F7'),
            ('Синий', '#2E6DD8'),
            ('Зеленый', '#2E8B57'),
            ('Титановый', '#8C7C6B'),
            ('Фиолетовый', '#7C3AED'),
            ('Red', '#FF3B30'),
            ('Purple', '#AF52DE'),
        ]
        out = []
        for name, hex_code in rows:
            obj, _ = Color.objects.get_or_create(name=name, defaults={'hex': hex_code})
            if not obj.hex:
                obj.hex = hex_code
                obj.save(update_fields=['hex'])
            out.append(obj)
        return out

    def _color_by_name(self, colors: list[Color], name: str) -> Color | None:
        for c in colors:
            if c.name == name:
                return c
        return None

    def _seed_sim_types(self) -> list[SimType]:
        out = []
        for name in ['eSIM', 'SIM+eSIM', 'SIM+SIM']:
            obj, _ = SimType.objects.get_or_create(name=name)
            out.append(obj)
        return out

    def _seed_products(
        self,
        categories: list[Category],
        brands: list[Brand],
        models: list[ProductModel],
        conditions: list[Condition],
    ) -> list[Product]:
        by_cat = {x.name: x for x in categories}
        by_brand = {x.name: x for x in brands}
        by_model = {x.name: x for x in models}
        by_condition = {x.name: x for x in conditions}

        products_data = [
            ('Apple iPhone 13', 'apple-iphone-13', 'Смартфоны', 'Apple', 'Apple iPhone 13', 'Новый', True, True),
            ('Apple iPhone 17 Pro Max', 'apple-iphone-17-pro-max', 'Смартфоны', 'Apple', 'Apple iPhone 17 Pro Max', 'Новый', True, True),
            ('Apple iPhone 17 Pro', 'apple-iphone-17-pro', 'Смартфоны', 'Apple', 'Apple iPhone 17 Pro', 'Новый', True, True),
            ('Apple iPhone 17', 'apple-iphone-17', 'Смартфоны', 'Apple', 'Apple iPhone 17', 'Новый', True, False),
            ('Apple iPhone 16e', 'apple-iphone-16e', 'Смартфоны', 'Apple', 'Apple iPhone 16e', 'Новый', True, False),
            ('Apple iPhone 16 Pro', 'apple-iphone-16-pro', 'Смартфоны', 'Apple', 'Apple iPhone 16 Pro', 'Новый', True, True),
            ('Б/у iPhone 13 Pro', 'bu-iphone-13-pro', 'Б/у техника', 'Apple', 'Apple iPhone 13 Pro', 'Б/у', False, False),
            ('Samsung Galaxy S26 Ultra', 'samsung-galaxy-s26-ultra', 'Смартфоны', 'Samsung', 'Samsung Galaxy S26 Ultra', 'Новый', True, True),
            ('Samsung Galaxy Z Fold7', 'samsung-galaxy-z-fold7', 'Смартфоны', 'Samsung', 'Samsung Galaxy Z Fold7', 'Новый', True, True),
            ('Samsung Galaxy Z Fold 6', 'samsung-galaxy-z-fold-6', 'Смартфоны', 'Samsung', 'Samsung Galaxy Z Fold 6', 'Уценка', True, False),
            ('Google Pixel 10 Pro XL', 'google-pixel-10-pro-xl', 'Смартфоны', 'Google', 'Google Pixel 10 Pro XL', 'Новый', True, False),
            ('Google Pixel 9 Pro', 'google-pixel-9-pro', 'Смартфоны', 'Google', 'Google Pixel 9 Pro', 'Новый', True, False),
            ('Xiaomi Redmi Note 14 Pro', 'xiaomi-redmi-note-14-pro', 'Смартфоны', 'Xiaomi', 'Xiaomi Redmi Note 14 Pro', 'Новый', True, False),
            ('Apple Watch Series 10', 'apple-watch-series-10', 'Смарт-часы', 'Apple', 'Apple iPhone 16 Pro', 'Новый', True, True),
            ('Apple AirPods Pro 3', 'apple-airpods-pro-3', 'Наушники', 'Apple', 'Apple iPhone 16 Pro', 'Новый', True, True),
            ('Sony WH-1000XM6', 'sony-wh-1000xm6', 'Наушники', 'Sony', 'Sony WH-1000XM6', 'Новый', True, True),
            ('Marshall Major V', 'marshall-major-v', 'Наушники', 'Marshall', 'Apple iPhone 16 Pro', 'Новый', False, False),
            ('Sony PlayStation 5 Slim', 'sony-playstation-5-slim', 'Игровые консоли', 'Sony', 'Apple iPhone 16 Pro', 'Новый', True, True),
            ('Valve Steam Deck OLED', 'valve-steam-deck-oled', 'Игровые консоли', 'Valve', 'Valve Steam Deck OLED', 'Новый', True, False),
            ('Dyson V15 Detect', 'dyson-v15-detect', 'Пылесосы', 'Dyson', 'Dyson V15 Detect', 'Новый', True, True),
            ('GoPro Hero 13 Black', 'gopro-hero-13-black', 'Камеры', 'GoPro', 'GoPro Hero 13', 'Новый', True, False),
            ('Canon EOS R6 Mark II', 'canon-eos-r6-mark-ii', 'Камеры', 'Canon', 'Canon EOS R6 Mark II', 'Новый', True, False),
            ('FUJIFILM X-T5', 'fujifilm-x-t5', 'Камеры', 'FUJIFILM', 'Canon EOS R6 Mark II', 'Новый', True, False),
            ('Yandex Station Max', 'yandex-station-max', 'Аксессуары', 'Yandex', 'Apple iPhone 16 Pro', 'Новый', True, False),
            ('iPad Pro 13 M4', 'ipad-pro-13-m4', 'Планшеты', 'Apple', 'Apple iPhone 17 Pro', 'Новый', True, True),
            ('MacBook Air M4', 'macbook-air-m4', 'Ноутбуки', 'Apple', 'Apple iPhone 17 Pro', 'Новый', True, True),
        ]

        out = []
        for title, slug, cat_name, brand_name, model_name, cond_name, is_new, is_hit in products_data:
            brand = by_brand.get(brand_name)
            category = by_cat.get(cat_name)
            if not brand or not category:
                continue
            obj, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'description': (
                        f'{title} — оригинальная техника с официальной гарантией. '
                        'Быстрая доставка по Санкт-Петербургу.'
                    ),
                    'article': f'SKU-{randint(10000, 99999)}',
                    'brand': brand,
                    'category': category,
                    'product_model': by_model.get(model_name),
                    'condition': by_condition.get(cond_name, conditions[0]),
                    'rating': round(uniform(4.2, 5.0), 1),
                    'is_available': True,
                    'is_new': is_new,
                    'is_hit': is_hit,
                    'is_bt': 'AirPods' in title or 'Marshall' in title,
                    **self._product_specs_for_category(category.name, title, brand_name, model_name),
                },
            )
            if not created:
                specs = self._product_specs_for_category(category.name, title, brand_name, model_name)
                for key, val in specs.items():
                    if val is not None:
                        setattr(obj, key, val)
                obj.save()
            out.append(obj)
        return list(Product.objects.all())

    def _product_specs_for_category(
        self,
        category_name: str,
        title: str,
        brand_name: str,
        model_name: str,
    ) -> dict:
        """Category-specific characteristics for admin + API specifications."""
        base = {
            'product_class': 'Premium',
            'line': brand_name,
            'series': model_name.split()[-1] if model_name else '',
        }
        if category_name == 'Смартфоны':
            return {
                **base,
                'type': 'Смартфон',
                'system': 'iOS' if brand_name == 'Apple' else 'Android',
                'diagonal': '6.1' if 'iPhone 13' in title else '6.7',
                'size': 'standard',
                'screen_type': 'OLED',
                'resolution': '2532×1170' if 'iPhone 13' in title else '2796×1290',
                'refresh_rate': '60 Hz' if 'iPhone 13' in title else '120 Hz',
                'density': '460 ppi',
                'brightness': '1200 nits',
                'glass': 'Ceramic Shield' if brand_name == 'Apple' else 'Gorilla Glass',
                'aod': 'Да' if brand_name == 'Apple' else 'Нет',
            }
        if category_name == 'Пылесосы':
            return {
                **base,
                'type': 'Пылесос',
                'system': 'Циклон',
                'version': 'V15 Detect',
                'line': 'V-series',
                'diagonal': None,
                'screen_type': None,
                'resolution': None,
                'refresh_rate': None,
                'density': None,
                'brightness': None,
                'glass': None,
                'aod': None,
            }
        if category_name == 'Наушники':
            return {
                **base,
                'type': 'Наушники',
                'line': title.split()[0] if title else brand_name,
                'series': 'Pro' if 'Pro' in title else 'Standard',
                'diagonal': None,
                'screen_type': None,
                'resolution': None,
                'refresh_rate': None,
                'density': None,
                'brightness': None,
                'glass': None,
                'aod': None,
            }
        if category_name == 'Игровые консоли':
            return {
                **base,
                'type': 'Консоль',
                'system': 'SteamOS' if 'Steam' in title else 'PlayStation OS',
                'version': 'OLED' if 'OLED' in title else 'Slim',
                'diagonal': '7"' if 'Steam' in title else None,
                'screen_type': 'OLED' if 'OLED' in title else None,
                'resolution': '1280×800' if 'Steam' in title else '4K',
                'refresh_rate': '90 Hz' if 'Steam' in title else '120 Hz',
                'density': None,
                'brightness': None,
                'glass': None,
                'aod': None,
            }
        if category_name == 'Аксессуары':
            return {
                **base,
                'type': 'Умная колонка' if 'Station' in title else 'Аксессуар',
                'size': 'compact',
                'line': brand_name,
                'diagonal': None,
                'screen_type': None,
                'resolution': None,
                'refresh_rate': None,
                'density': None,
                'brightness': None,
                'glass': None,
                'aod': None,
            }
        return {
            **base,
            'type': category_name,
            'diagonal': None,
            'size': 'standard',
            'screen_type': None,
            'resolution': None,
            'refresh_rate': None,
            'density': None,
            'brightness': None,
            'glass': None,
            'aod': None,
        }

    def _seed_variants(
        self,
        products: list[Product],
        memories: list[Memory],
        colors: list[Color],
        sim_types: list[SimType],
    ) -> list[ProductVariant]:
        out = []
        sim_main = sim_types[0]
        memory_128 = next((m for m in memories if '128' in m.name), memories[0])
        iphone_palette = [
            self._color_by_name(colors, 'Green'),
            self._color_by_name(colors, 'Blue'),
            self._color_by_name(colors, 'Starlight'),
            self._color_by_name(colors, 'Midnight'),
        ]
        iphone_palette = [c for c in iphone_palette if c]

        for p in products:
            if p.category.name == 'Смартфоны':
                palette = (
                    iphone_palette
                    if p.slug == 'apple-iphone-13'
                    else [colors[(i + p.id) % len(colors)] for i in range(4)]
                )
                for i, color in enumerate(palette):
                    memory = memory_128 if p.slug == 'apple-iphone-13' else memories[min(i, len(memories) - 1)]
                    base_price = 43500.0 if p.slug == 'apple-iphone-13' else float(randint(49999, 149999))
                    discount = 0 if p.slug == 'apple-iphone-13' else choice([0, 5, 8, 10])
                    old_price = None if p.slug == 'apple-iphone-13' else float(base_price + randint(2000, 8000))
                    obj, created = ProductVariant.objects.get_or_create(
                        product=p,
                        memory=memory,
                        color=color,
                        defaults={
                            'price': base_price,
                            'old_price': old_price,
                            'discount': discount or None,
                            'is_available': True,
                            'description': f'{p.title} / {memory.name} / {color.name}',
                            'images': None,
                            'diagonal': p.diagonal or '6.1',
                            'size': p.size or 'standard',
                            'sim_type': sim_main,
                        },
                    )
                    if not created:
                        obj.price = base_price
                        obj.old_price = old_price
                        obj.discount = discount or None
                        obj.images = None
                        obj.is_available = True
                        obj.save()
                    out.append(obj)
                    for st in sim_types:
                        ProductVariantSimType.objects.get_or_create(
                            product_variant=obj,
                            sim_type=st,
                            defaults={'price': round(obj.price + uniform(0, 200), 2)},
                        )
                continue

            variant_count = 2
            for i in range(variant_count):
                memory = memories[min(i + (p.id % 2), len(memories) - 1)]
                color = colors[(i + p.id) % len(colors)]
                base_price = float(randint(499, 4999))
                discount = choice([0, 5, 8, 10, 12, 15])
                old_price = float(base_price + randint(200, 800)) if discount else None
                defaults = {
                    'memory': memory,
                    'color': color,
                    'price': base_price,
                    'old_price': old_price,
                    'discount': discount or None,
                    'is_available': choice([True, True, True, False]),
                    'description': f'{p.title} / {memory.name} / {color.name}',
                    'images': None,
                    'diagonal': p.diagonal,
                    'size': p.size or 'standard',
                    'sim_type': sim_main,
                }
                obj, created = ProductVariant.objects.get_or_create(
                    product=p,
                    memory=memory,
                    color=color,
                    defaults=defaults,
                )
                if not created:
                    for key, val in defaults.items():
                        setattr(obj, key, val)
                    obj.save()
                out.append(obj)
                for st in sim_types:
                    ProductVariantSimType.objects.get_or_create(
                        product_variant=obj,
                        sim_type=st,
                        defaults={'price': round(obj.price + uniform(0, 200), 2)},
                    )
        return out

    def _seed_product_images(self, products: list[Product], variants: list[ProductVariant]) -> None:
        """Gallery images linked to color (Whale Store: photos change when color is selected)."""
        variants_by_product: dict[int, list[ProductVariant]] = {}
        for v in variants:
            variants_by_product.setdefault(v.product_id, []).append(v)

        for p in products:
            product_variants = variants_by_product.get(p.id, [])
            seen_colors: dict[int, Color] = {}
            for v in product_variants:
                if v.color_id and v.color_id not in seen_colors:
                    seen_colors[v.color_id] = v.color

            if seen_colors:
                for color_id, color in seen_colors.items():
                    slug_color = color.name.lower().replace(' ', '-').replace('/', '-')
                    image_count = 4 if p.slug == 'apple-iphone-13' else 3
                    for i in range(image_count):
                        path = f'uploads/image/demo-{p.slug}-{slug_color}-{i + 1}.png'
                        ProductImage.objects.update_or_create(
                            product=p,
                            color_id=color_id,
                            sort_order=i,
                            defaults={
                                'image': path,
                                'alt': f'{p.title} — {color.name}',
                                'is_primary': i == 0,
                            },
                        )
                continue

            for i in range(2):
                path = f'uploads/image/demo-{p.slug}-shared-{i + 1}.png'
                ProductImage.objects.update_or_create(
                    product=p,
                    color_id=None,
                    sort_order=i,
                    defaults={
                        'image': path,
                        'alt': p.title,
                        'is_primary': i == 0,
                    },
                )

    def _seed_orders(self, variants: list[ProductVariant]) -> None:
        from apps.store_core.models import OrderItem, StoreOrder

        users = list(StoreUser.objects.all()[:5])
        if not users or not variants:
            return
        for idx, user in enumerate(users):
            picked = variants[idx * 2:(idx * 2) + 2] or variants[:2]
            total = int(sum(v.price for v in picked))
            order, created = StoreOrder.objects.get_or_create(
                email=user.email,
                total_sum=total,
                delivery_type=StoreOrder.DeliveryType.DELIVERY if idx % 2 == 0 else StoreOrder.DeliveryType.PICKUP,
                defaults={
                    'full_name': f'{user.first_name} {user.last_name}'.strip() or user.email,
                    'phone': user.phone or '+79000000000',
                    'apartment': '12',
                    'entrance': '2',
                    'floor': '5',
                    'products': [],
                },
            )
            if not created or order.items.exists():
                continue
            running = 0
            for v in picked:
                line = int(v.price)
                OrderItem.objects.create(
                    order=order,
                    product_variant=v,
                    quantity=1,
                    unit_price=int(v.price),
                    line_total=line,
                )
                running += line
            if order.total_sum != running:
                order.total_sum = running
                order.save(update_fields=['total_sum'])

    def _seed_blog(self) -> None:
        categories = ['Новинки', 'Обзоры техники', 'Гайды и советы']
        blog_categories = [BlogCategory.objects.get_or_create(name=name)[0] for name in categories]
        posts = [
            ('В каталог добавлены новые модели iPhone 17', 'novye-modeli-iphone-17-v-kataloge'),
            ('Как выбрать смартфон в 2026 году', 'kak-vybrat-smartfon-2026'),
            ('Лучшие наушники для музыки и работы', 'luchshie-naushniki-dlya-muzyki'),
            ('Trade-in: как обменять старый iPhone', 'trade-in-kak-obmenyat-iphone'),
            ('Обзор Samsung Galaxy Z Fold7', 'obzor-samsung-galaxy-z-fold7'),
        ]
        for idx, (title, slug) in enumerate(posts):
            blog, _ = Blog.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'content': (
                        'Демо-статья для админ-панели. '
                        'Здесь может быть полный текст новости или обзора.'
                    ),
                    'blog_category': blog_categories[idx % len(blog_categories)],
                    'image': f'uploads/image/blog-{idx + 1}.png',
                },
            )
            for step_no in range(1, 4):
                BlogSteps.objects.get_or_create(
                    blog=blog,
                    title=f'Шаг {step_no}',
                    defaults={'content': f'Содержимое шага {step_no} для статьи «{blog.title}».'},
                )

    def _seed_repair(self) -> None:
        sb_apple, _ = ServiceBrand.objects.update_or_create(
            slug='apple-service',
            defaults={'name': 'Apple', 'image': 'uploads/image/service-apple.png'},
        )
        sb_samsung, _ = ServiceBrand.objects.update_or_create(
            slug='samsung-service',
            defaults={'name': 'Samsung', 'image': 'uploads/image/service-samsung.png'},
        )
        models = []
        for name, slug, brand in [
            ('iPhone 16 Pro Max', 'iphone-16-pro-max', sb_apple),
            ('iPhone 17 Pro', 'iphone-17-pro', sb_apple),
            ('Galaxy S26 Ultra', 'galaxy-s26-ultra', sb_samsung),
            ('Galaxy Z Fold7', 'galaxy-z-fold7', sb_samsung),
        ]:
            sm, _ = ServiceModel.objects.update_or_create(
                slug=slug,
                defaults={'name': name, 'service_brand': brand},
            )
            models.append(sm)
        for sm in models:
            for svc_name, suffix, labor in [
                ('Замена экрана', 'ekran', 12000),
                ('Замена батареи', 'battery', 7000),
                ('Ремонт камеры', 'camera', 8500),
                ('Замена разъёма зарядки', 'port', 5500),
            ]:
                Service.objects.update_or_create(
                    slug=f'{sm.slug}-{suffix}',
                    defaults={
                        'name': svc_name,
                        'service_model': sm,
                        'labor_only': labor,
                        'labor_with_part': labor + 6000,
                    },
                )

    def _seed_banners_and_info(self) -> None:
        banners = [
            (
                'Оригинальная техника с быстрой доставкой в Санкт-Петербурге',
                'Бесплатная доставка по городу в день заказа.',
            ),
            (
                'Рассрочка без переплат на всю технику!',
                'Оформление за 5 минут — партнёрские банки.',
            ),
            (
                'iPhone 17 Pro Max уже в продаже',
                'Новый уровень мощности с Apple A19 Pro.',
            ),
        ]
        for idx, (title, description) in enumerate(banners):
            Banner.objects.update_or_create(
                title=title,
                defaults={
                    'description': description,
                    'img_pc': f'uploads/image/banner-{idx + 1}-pc.png',
                    'img_mobile': f'uploads/image/banner-{idx + 1}-mobile.png',
                },
            )

        advantages = [
            ('Гарантия магазина', '365 дней гарантии на всю технику'),
            ('Выездной сервис', 'Специалисты приедут в удобное время'),
            ('Быстрая доставка', 'По Санкт-Петербургу в день заказа'),
            ('Trade-in', 'Обменяйте старое устройство на новое'),
            ('Оригинальная техника', 'Только проверенные поставщики'),
            ('Рассрочка 0%', 'Без переплат на 12 месяцев'),
        ]
        for name, description in advantages:
            Info.objects.update_or_create(name=name, defaults={'description': description})

    def _seed_storefront(self, variants: list[ProductVariant]) -> None:
        users = list(StoreUser.objects.all())
        for user in users:
            for v in variants[:5]:
                Favorite.objects.get_or_create(user_id=user.id, variant_id=v.id)

        for user in users[:5]:
            for idx, v in enumerate(variants[:3], start=1):
                CartItem.objects.get_or_create(
                    user_id=user.id,
                    variant_id=v.id,
                    defaults={'quantity': idx},
                )

        reviews = [
            ('Алексей', 'Покупал iPhone, всё отлично, доставка в день заказа.', 5, Review.SOURCE_AVITO),
            ('Марина', 'Сервис и поддержка на высоте, помогли с выбором.', 5, Review.SOURCE_YANDEX),
            ('Камрон', 'Удобный сайт и честные цены. Буду брать ещё.', 4, Review.SOURCE_SITE),
            ('Дмитрий', 'Видео-отзыв о покупке и магазине.', 5, Review.SOURCE_SITE),
            ('Ольга', 'Отличный trade-in, быстро оценили мой старый телефон.', 5, Review.SOURCE_YANDEX),
            ('Сергей', 'Samsung Galaxy Z Fold7 — мечта сбылась!', 5, Review.SOURCE_AVITO),
        ]
        for idx, (author, text, rating, source) in enumerate(reviews):
            Review.objects.update_or_create(
                author_name=author,
                text=text,
                source=source,
                defaults={
                    'rating': rating,
                    'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' if idx == 3 else '',
                    'thumbnail': f'uploads/image/review-{idx + 1}.png',
                    'is_published': True,
                },
            )

        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        settings.phone = '+7 (966) 861-52-42'
        settings.email = 'info@geniusstore.ru'
        settings.address = 'Санкт-Петербург, Невский проспект 112-114'
        settings.telegram_url = 'https://t.me/genius_store'
        settings.vk_url = 'https://vk.com/genius_store'
        settings.whatsapp_url = 'https://wa.me/79668615242'
        settings.map_lat = 59.9343
        settings.map_lng = 30.3351
        settings.advantages = [
            {'title': 'Гарантия магазина', 'description': '365 дней гарантии на всю технику', 'icon': 'shield'},
            {'title': 'Выездной сервис', 'description': 'Наши специалисты приедут в удобное время', 'icon': 'service'},
            {'title': 'Быстрая доставка', 'description': 'По Санкт-Петербургу в день заказа', 'icon': 'delivery'},
            {'title': 'Trade-in техники', 'description': 'Обменяйте старое устройство на новое', 'icon': 'tradein'},
        ]
        settings.save()
