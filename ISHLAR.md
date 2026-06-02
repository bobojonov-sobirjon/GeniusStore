# Genius Store — qilingan ishlar

Backend: Django 5 + DRF, admin: Jazzmin, deploy: `https://admin.geniusstorerf.ru`

---

## 1. Django Admin (Whale Store uslubi)

- **Jazzmin** yengil tema, sidebar tartibi (`config/settings.py`)
- Maxsus CSS/JS: `static/admin/css/custom_admin.css`, `static/admin/js/admin_drawer.js`
- Admin shablonlari: `templates/admin/whale/change_form.html`, `change_list.html`
- Mahsulot formasi: fieldsets, `ProductImage` inline, `ProductVariantAdmin` (narxlar)
- `/admin/accounts/customuser/` → `/admin/store_core/storeuser/` redirect
- Admin uchun JSON 404 middleware o‘chirilgan (`/admin/`, `/docs/`)

---

## 2. Test ma’lumotlari (seed)

Buyruq:

```bash
python manage.py seed_fake_data --with-superuser
```

- Admin: `admin` / `admin123`
- Demo foydalanuvchi: `demo1@geniusstore.local` / `12345678`
- Brendlar, mahsulotlar, variantlar, bannerlar, sharhlar va boshqalar yaratiladi

---

## 3. Production CSRF / CORS

`CSRF_TRUSTED_ORIGINS` va `CORS_ALLOWED_ORIGINS` ga qo‘shildi:

- `https://admin.geniusstorerf.ru`
- `https://geniusstorerf.ru`
- `https://www.geniusstorerf.ru`

---

## 4. Swagger — foydalanuvchi taglari

Bitta **«Пользователи»** tag quyidagilarga bo‘lingan:

- Список
- Регистрация
- Авторизация
- Профиль
- Пароль
- Управление

---

## 5. API 500 xatolari (async)

**Sabab:** DRF `APIView` async handlerlarni `await` qilmaydi → `AssertionError: received <class 'coroutine'>`.

**Yechim:** `apps/common/views.py` — async-aware `APIView`. Barcha view fayllar shu bazadan import qiladi.

Qo‘shimcha:

- `apps/catalog/serialization.py` — null/NaN xavfsizligi
- `config/middleware/middleware.py` — API xatolarida to‘liq traceback log
- `Banner.created_at` db_column tuzatildi (`reatedAt` → `createdAt`), migration `0005`

---

## 6. Rasm URL — base URL (frontend talabi)

**Muammo:** API faqat nisbiy yo‘l qaytarardi: `/uploads/image/banner-3-pc.png`

**Yechim:**

| Fayl | Vazifa |
|------|--------|
| `apps/common/media_urls.py` | `media_url()`, `serialize_values_row()` |
| `config/settings.py` | `PUBLIC_MEDIA_BASE_URL` (default: `https://admin.geniusstorerf.ru`) |
| `apps/site_content/site_sync.py` | Banner `img_pc`, `img_mobile` |
| `apps/blog/blog_sync.py` | Blog `image` |
| `apps/repair/repair_sync.py` | Service brand `image` |
| `apps/storefront/storefront_sync.py` | Video `thumbnail`, kategoriya `icon`, mahsulot `image` |

**Natija (misol):**

```json
{
  "img_pc": "https://admin.geniusstorerf.ru/media/uploads/image/banner-3-pc.png",
  "img_mobile": "https://admin.geniusstorerf.ru/media/uploads/image/banner-3-mobile.png"
}
```

Server `.env` (ixtiyoriy):

```env
PUBLIC_MEDIA_BASE_URL=https://admin.geniusstorerf.ru
```

---

## 7. Blog va Service Brand — 500 tuzatish

**Endpointlar:**

- `GET /api/blog/{id}`
- `GET /api/service-brand/{id}`

**O‘zgarish:** UUID va datetime to‘g‘ri serialize qilinadi, rasmlar to‘liq URL bilan qaytadi (`blog_sync.py`, `repair_sync.py`).

---

## 8. Frontend API xaritasi

### Banner (birinchi rasm)

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/banner` | Yo‘q |
| GET | `/api/banner/{id}` | Yo‘q |

### Kategoriya rasmlari (500 bo‘lgan joy)

| Method | Endpoint | Maydon |
|--------|----------|--------|
| GET | `/api/site/settings` | `categories[].icon` — endi to‘liq URL |

### Qidiruv (3-rasm)

| Method | Endpoint | Maqsad |
|--------|----------|--------|
| GET | `/api/product/search/{query}` | To‘liq qidiruv (katalog) |
| GET | `/api/product/search/{query}/suggest` | Header qidiruv: mahsulotlar + taglar |

### «Популярные запросы» (4-rasm)

| Method | Endpoint | Maydon |
|--------|----------|--------|
| GET | `/api/site/settings` | `popularSearches` — hit mahsulot nomlari |

**Misol javob:**

```json
{
  "popularSearches": [
    "iPhone 17 Pro Max",
    "Samsung Galaxy S26",
    "MacBook Air M3"
  ]
}
```

### Video-otzyvy (4-rasm — «Видео-отзывы»)

| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/api/reviews/videos?page=1&limit=4` | Yo‘q |

**Javob maydonlari:** `id`, `authorName`, `videoUrl`, `thumbnail`, `rating`, `createdAt`

### «Новости» — yangiliklar bloki (asosiy sahifa)

Swagger’da **«Блог — Статьи»** tag ostida. Alohida `/api/news` modeli yo‘q — bu **Blog** API.

| UI | Method | Endpoint | Auth |
|----|--------|----------|------|
| 4 ta kartochka (asosiy sahifa) | GET | `/api/blog/all/1/4` yoki `/api/news/all/1/4` | Yo‘q |
| «Все новости →» sahifasi | GET | `/api/blog/all/{page}/{limit}` | Yo‘q |
| Yangilik ochish (slug) | GET | `/api/blog/slug/{slug}` yoki `/api/news/slug/{slug}` | Yo‘q |
| UUID bo‘yicha | GET | `/api/blog/{uuid}` yoki `/api/news/{uuid}` | Yo‘q |
| «Другие новости» (batafsil sahifa) | GET | `/api/blog/slug/{slug}/related?limit=3` | Yo‘q |

**Kartochka uchun kerakli maydonlar** (`data[]` ichida):

| Maydon | UI |
|--------|-----|
| `title` | Sarlavha |
| `image` | Rasm (to‘liq URL) |
| `createdAt` | Sana — frontend `23.02.2026` formatiga o‘tkazadi |
| `slug` | Havola: `/news/{slug}` |
| `id` | UUID |

**Misol:**

```
GET https://admin.geniusstorerf.ru/api/news/all/1/4
```

```json
{
  "data": [
    {
      "id": "6806cbca-a46f-4782-a3ce-64fd149b822e",
      "title": "Новый iPhone уже в продаже",
      "slug": "novyy-iphone-uzhe-v-prodazhe",
      "image": "https://admin.geniusstorerf.ru/media/uploads/image/...",
      "createdAt": "2026-02-23T10:00:00Z",
      "content": "...",
      "blogCategoryId": "...",
      "blogSteps": []
    }
  ],
  "count": 12
}
```

### Korzinka — karzinka (5-rasm)

| Method | Endpoint | Body | Auth |
|--------|----------|------|------|
| GET | `/api/cart` | — | **Cookie `access_token`** |
| POST | `/api/cart` | `{"variantId": "uuid", "quantity": 1}` | Cookie |
| PATCH | `/api/cart/{variant_id}` | `{"quantity": 2}` | Cookie |
| DELETE | `/api/cart/{variant_id}` | — | Cookie |
| DELETE | `/api/cart` | — | Cookie (tozalash) |

### Buyurtma (Order) — yangi soddalashtirilgan API

Eski `send-order2/3/4`, `quick-order` **o‘chirildi**.

| Method | Endpoint | Auth |
|--------|----------|------|
| POST | `/api/order` | Cookie `access_token` |
| GET | `/api/order` | Cookie — faqat o‘z buyurtmalari |
| GET | `/api/order/{uuid}` | Cookie — faqat o‘z buyurtmasi |

**POST body:**
```json
{
  "products_list": [
    { "product_id": "variant-uuid", "quantity": 2 }
  ],
  "isDelivery": true,
  "isPickup": false,
  "apartment": "12",
  "entrance": "2",
  "floor": "5"
}
```

**Response:** `id`, `totalPrice`, `isDelivery`, `isPickup`, `products_list[]`, `apartment`, `entrance`, `floor`

Admin: **Заказы** — pozitsiyalar inline jadvalda.

**403 sababi:** Login qilinmagan. Swagger’da cookie bo‘lmasa `"Учетные данные не были предоставлены."` — bu normal.

**Frontend oqimi:**

1. `POST /api/auth/login` — cookie olinadi
2. `POST /api/cart` — mahsulot qo‘shish
3. `GET /api/cart` — savat + `totalPrice` + badge uchun `count`

### Boshqa foydali endpointlar

| UI | Endpoint |
|----|----------|
| Mahsulotlar ro‘yxati | `GET /api/product/all/{page}/{limit}` |
| Blog slug bo‘yicha | `GET /api/blog/slug/{slug}` |
| Bog‘liq yangiliklar | `GET /api/blog/slug/{slug}/related` |
| Izbrannoe | `GET/POST /api/favorites` (cookie kerak) |
| Sayt sozlamalari | `GET /api/site/settings` |

---

## 9. Deploy (server)

```bash
cd /var/www/GeniusStore
git pull
source env/bin/activate
python manage.py migrate
sudo systemctl restart geniusstore
sudo journalctl -u geniusstore -n 50 --no-pager
```

PostgreSQL DB nomi serverda: **`genius-store`**

---

## 10. O‘zgartirilgan asosiy fayllar

```
apps/common/media_urls.py          # yangi
apps/common/views.py               # async APIView
apps/site_content/site_sync.py     # banner URL
apps/blog/blog_sync.py             # blog serialize + URL
apps/repair/repair_sync.py         # service brand serialize + URL
apps/storefront/storefront_sync.py # popularSearches, thumbnail, icon
config/settings.py                 # PUBLIC_MEDIA_BASE_URL, Jazzmin, CSRF
static/admin/css/custom_admin.css
static/admin/js/admin_drawer.js
templates/admin/whale/
apps/store_core/admin.py
config/middleware/middleware.py
apps/catalog/serialization.py
```

---

## 11. Swagger eslatmalari

- Ba’zi endpointlarda `unable to guess serializer` — kosmetik ogohlantirish, API ishlaydi
- Korzina va izbrannoe Swagger’da qulf belgisi — autentifikatsiya talab qilinadi
- Qidiruv suggest: tag **storefront** bo‘limida (`/api/product/search/.../suggest`)
- To‘liq qidiruv: tag **katalog** bo‘limida (`/api/product/search/{query}`)
