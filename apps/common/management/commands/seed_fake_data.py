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
        self._seed_product_images(products)
        self._seed_orders(variants)
        self._seed_blog()
        self._seed_repair()
        self._seed_banners_and_info()
        self._seed_storefront(variants)
        self.stdout.write(self.style.SUCCESS('Fake data seeded successfully.'))
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
                    'avatar': '/uploads/image/user-default.png',
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
            obj, _ = Category.objects.get_or_create(name=name, defaults={'slug': slug, 'icon': ''})
            if not obj.slug:
                obj.slug = slug
                obj.save(update_fields=['slug'])
            out.append(obj)
        return out

    def _seed_brands(self) -> list[Brand]:
        names = [
            'Apple', 'Samsung', 'Dyson', 'Sony', 'Valve', 'Yandex',
            'Canon', 'FUJIFILM', 'GoPro', 'Marshall', 'Google', 'Xiaomi',
        ]
        out = []
        for name in names:
            obj, _ = Brand.objects.get_or_create(name=name)
            out.append(obj)
        return out

    def _seed_product_models(self) -> list[ProductModel]:
        names = [
            'Apple iPhone 17', 'Apple iPhone 17 Pro', 'Apple iPhone 17 Pro Max',
            'Apple iPhone 16 Pro', 'Apple iPhone 16e', 'Apple iPhone 13 Pro',
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
            ('Silver', '#C0C0C0'),
            ('Blue', '#2563EB'),
            ('Orange', '#F97316'),
            ('Cosmic Orange', '#EA580C'),
            ('Черный', '#0F0F0F'),
            ('Белый', '#F7F7F7'),
            ('Синий', '#2E6DD8'),
            ('Зеленый', '#2E8B57'),
            ('Титановый', '#8C7C6B'),
            ('Фиолетовый', '#7C3AED'),
        ]
        out = []
        for name, hex_code in rows:
            obj, _ = Color.objects.get_or_create(name=name, defaults={'hex': hex_code})
            if not obj.hex:
                obj.hex = hex_code
                obj.save(update_fields=['hex'])
            out.append(obj)
        return out

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
                    'type': 'Смартфон' if category.name == 'Смартфоны' else category.name,
                    'product_class': 'Premium' if is_hit else 'Standard',
                    'line': brand_name,
                    'series': model_name.split()[-1] if model_name else '',
                    'system': 'iOS' if brand_name == 'Apple' else 'Android',
                    'diagonal': '6.9' if 'iPhone' in title else '6.7',
                    'size': 'standard',
                    'screen_type': 'OLED',
                    'resolution': '2796x1290',
                    'refresh_rate': '120 Hz',
                    'density': '460 ppi',
                    'brightness': '2000 nits',
                    'glass': 'Ceramic Shield' if brand_name == 'Apple' else 'Gorilla Glass',
                    'aod': 'Да' if 'iPhone' in title else 'Нет',
                },
            )
            out.append(obj)
            if not created:
                continue
        return list(Product.objects.all())

    def _seed_variants(
        self,
        products: list[Product],
        memories: list[Memory],
        colors: list[Color],
        sim_types: list[SimType],
    ) -> list[ProductVariant]:
        out = []
        sim_main = sim_types[0]
        for p in products:
            variant_count = 3 if p.category.name == 'Смартфоны' else 2
            for i in range(variant_count):
                memory = memories[min(i + (p.id % 2), len(memories) - 1)]
                color = colors[(i + p.id) % len(colors)]
                base_price = randint(2999, 8999) if p.category.name == 'Смартфоны' else randint(499, 4999)
                discount = choice([0, 5, 8, 10, 12, 15])
                old_price = float(base_price + randint(200, 800)) if discount else None
                defaults = {
                    'memory': memory,
                    'color': color,
                    'price': float(base_price),
                    'old_price': old_price,
                    'discount': discount or None,
                    'is_available': choice([True, True, True, False]),
                    'description': f'{p.title} / {memory.name} / {color.name}',
                    'images': [
                        {'id': f'{p.slug}-{i}-1', 'url': f'/uploads/image/{p.slug}-{i}-1.png'},
                        {'id': f'{p.slug}-{i}-2', 'url': f'/uploads/image/{p.slug}-{i}-2.png'},
                    ],
                    'diagonal': p.diagonal or '6.7',
                    'size': p.size or 'standard',
                    'sim_type': sim_main,
                }
                obj, _ = ProductVariant.objects.get_or_create(
                    product=p,
                    memory=memory,
                    color=color,
                    defaults=defaults,
                )
                if obj.price == 0:
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

    def _seed_product_images(self, products: list[Product]) -> None:
        for p in products:
            for i in range(2):
                path = f'image/demo-{p.slug}-{i + 1}.png'
                ProductImage.objects.get_or_create(
                    product=p,
                    path=path,
                    defaults={
                        'alt': p.title,
                        'sort_order': i,
                        'is_primary': i == 0,
                    },
                )

    def _seed_orders(self, variants: list[ProductVariant]) -> None:
        users = list(StoreUser.objects.all()[:5])
        if not users or not variants:
            return
        for idx, user in enumerate(users):
            picked = variants[idx * 2:(idx * 2) + 2] or variants[:2]
            total = int(sum(v.price for v in picked))
            StoreOrder.objects.get_or_create(
                user=user,
                total_sum=total,
                defaults={
                    'products': [
                        {
                            'variantId': str(v.id),
                            'title': v.product.title,
                            'qty': 1,
                            'price': v.price,
                        }
                        for v in picked
                    ],
                },
            )

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
            blog, _ = Blog.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'content': (
                        'Демо-статья для админ-панели. '
                        'Здесь может быть полный текст новости или обзора.'
                    ),
                    'blog_category': blog_categories[idx % len(blog_categories)],
                    'image': f'/uploads/image/blog-{idx + 1}.png',
                },
            )
            for step_no in range(1, 4):
                BlogSteps.objects.get_or_create(
                    blog=blog,
                    title=f'Шаг {step_no}',
                    defaults={'content': f'Содержимое шага {step_no} для статьи «{blog.title}».'},
                )

    def _seed_repair(self) -> None:
        sb_apple, _ = ServiceBrand.objects.get_or_create(
            slug='apple-service',
            defaults={'name': 'Apple', 'image': '/uploads/image/service-apple.png'},
        )
        sb_samsung, _ = ServiceBrand.objects.get_or_create(
            slug='samsung-service',
            defaults={'name': 'Samsung', 'image': '/uploads/image/service-samsung.png'},
        )
        models = []
        for name, slug, brand in [
            ('iPhone 16 Pro Max', 'iphone-16-pro-max', sb_apple),
            ('iPhone 17 Pro', 'iphone-17-pro', sb_apple),
            ('Galaxy S26 Ultra', 'galaxy-s26-ultra', sb_samsung),
            ('Galaxy Z Fold7', 'galaxy-z-fold7', sb_samsung),
        ]:
            sm, _ = ServiceModel.objects.get_or_create(slug=slug, defaults={'name': name, 'service_brand': brand})
            models.append(sm)
        for sm in models:
            for svc_name, suffix, labor in [
                ('Замена экрана', 'ekran', 12000),
                ('Замена батареи', 'battery', 7000),
                ('Ремонт камеры', 'camera', 8500),
                ('Замена разъёма зарядки', 'port', 5500),
            ]:
                Service.objects.get_or_create(
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
            Banner.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'img_pc': f'/uploads/image/banner-{idx + 1}-pc.png',
                    'img_mobile': f'/uploads/image/banner-{idx + 1}-mobile.png',
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
            Info.objects.get_or_create(name=name, defaults={'description': description})

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
            Review.objects.get_or_create(
                author_name=author,
                text=text,
                source=source,
                defaults={
                    'rating': rating,
                    'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' if idx == 3 else '',
                    'thumbnail': f'/uploads/image/review-{idx + 1}.png',
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
