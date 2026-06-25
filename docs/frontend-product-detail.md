# Карточка товара — интеграция для фронтенда

Документ описывает API страницы товара (как на Whale Store): выбор цвета, памяти, типа SIM, галерея по цвету, характеристики и цена.

**Базовый URL API:** `https://admin.geniusstorerf.ru/api`  
**Swagger:** `https://admin.geniusstorerf.ru/api/schema/swagger-ui/`

---

## 1. Главный endpoint

```
GET /api/product/slug/{slug}
```

Альтернатива по числовому id (те же query-параметры):

```
GET /api/product/{id}
```

Пример:

```
GET /api/product/slug/apple-iphone-13
```

---

## 2. Query-параметры (фильтр варианта)

Фильтрацию варианта делает **бэкенд**. Фронт не пересчитывает цену и не подбирает картинки на клиенте — только отправляет выбор пользователя в query.

| Параметр    | Тип    | Обязательный | Описание |
|------------|--------|--------------|----------|
| `colorId`  | number | нет          | ID цвета из `colors[].id` |
| `memoryId` | number | нет          | ID памяти из `colors[].memories[].memoryId` |
| `simTypeId`| UUID   | нет          | ID типа SIM из `selectedVariant.simTypes[].simTypeId` |

### Примеры запросов

```http
# Первая загрузка страницы (без фильтра — сервер выберет первый вариант)
GET /api/product/slug/apple-iphone-13

# Пользователь выбрал зелёный цвет
GET /api/product/slug/apple-iphone-13?colorId=13

# Цвет + память
GET /api/product/slug/apple-iphone-13?colorId=13&memoryId=1

# Цвет + память + тип SIM (цена берётся из simTypes)
GET /api/product/slug/apple-iphone-13?colorId=2&memoryId=1&simTypeId=40b098b1-d719-4590-b235-20370c2ae3bf
```

### Ошибки

| Код | Когда |
|-----|--------|
| `404` | Товар с таким `slug` не найден |
| `400` | Неверный формат параметра или комбинация не существует (`Вариант не найден: colorId=..., memoryId=...`) |

---

## 3. Структура ответа (важные поля)

```json
{
  "id": 28,
  "title": "Apple iPhone 13",
  "slug": "apple-iphone-13",
  "brand": { "id": 1, "name": "Apple", "image": "..." },
  "category": { "id": 1, "name": "Смартфоны", "slug": "smartfony" },

  "images": [],
  "colors": [],
  "specFields": [],
  "specifications": [],
  "variants": [],

  "selection": {
    "colorId": null,
    "memoryId": null,
    "simTypeId": null
  },
  "selectedVariant": {}
}
```

### Назначение полей

| Поле | Для чего на UI |
|------|----------------|
| `colors[]` | Блок выбора **цвета**: кружки с `hex`, список памяти и цен по каждому цвету |
| `colors[].images` | Превью галереи для конкретного цвета (можно показать при hover) |
| `colors[].memories[]` | Кнопки **памяти** внутри выбранного цвета: `name`, `price`, `variantId` |
| `images` | **Главная галерея** на странице — всегда соответствует `selectedVariant` |
| `selectedVariant` | Текущий выбранный вариант: цена, `id` для корзины, SIM-типы, картинки |
| `selectedVariant.simTypes[]` | Переключатель **SIM / eSIM** с отдельными ценами |
| `specifications` | Таблица характеристик для **текущего** варианта |
| `specFields` | Какие ключи характеристик показывать для категории товара |
| `variants[]` | Полный список всех комбинаций (для отладки или сложной логики; на UI обычно достаточно `colors` + `selectedVariant`) |
| `selection` | Эхо переданных query-параметров |
| `characteristicGroups` | **Полные характеристики** (группы → строки → значения), см. раздел 14 |
| `specifications` | Краткая таблица для карточки (старый формат, flat) |

---

## 14. Характеристики (группы — Whale Store)

Полный блок «Характеристики» на странице товара приходит в `characteristicGroups`.

### Структура

```json
"characteristicGroups": [
  {
    "id": "uuid-группы",
    "title": "Корпус",
    "sortOrder": 2,
    "items": [
      {
        "id": "uuid-строки",
        "label": "Материал",
        "values": ["алюминий"],
        "source": "manual",
        "isVariant": false
      },
      {
        "label": "Память",
        "values": ["128 GB"],
        "source": "memory",
        "isVariant": true
      },
      {
        "label": "Функции камеры",
        "values": [
          "ночной режим",
          "Smart HDR 4",
          "панорамная съёмка"
        ],
        "source": "manual",
        "isVariant": false
      }
    ]
  }
]
```

### 3 уровня (как на сайте Whale Store)

| Уровень | Поле API | UI |
|---------|----------|-----|
| Главная группа | `title` | Левая колонка: «Корпус», «Камера», «Дисплей» |
| Под-характеристика | `items[].label` | Средняя колонка: «Материал», «Вес, г» |
| Значение(я) | `items[].values` | Правая колонка: текст или `<ul>` если `values.length > 1` |

### Вариант-зависимые строки

Если `isVariant: true`, значения меняются при смене цвета/памяти/SIM (тот же query `colorId`, `memoryId`, `simTypeId`):

| `source` | Откуда берётся значение |
|----------|-------------------------|
| `memory` | Память выбранного варианта |
| `color` | Цвет выбранного варианта |
| `sim` | Тип SIM (с учётом `simTypeId` в query) |
| `series` | Поле `series` товара |
| `model` | Модель товара |
| `condition` | Состояние |
| `system` | ОС (`iOS` и т.д.) |
| `manual` | Задано в админке вручную |

Строки с `isVariant: true` можно подсвечивать (как «Серия», «Память», «Цвет» на референсе).

### Как заполнять в админке

На странице редактирования товара — вкладка **«Характеристики»** (одна плоская таблица):

| Колонка | Что указать |
|---------|-------------|
| **Тип** | Блок на сайте: «Основные характеристики», «Процессор», «Корпус», «Заводские данные» и т.д. |
| **Порядок** | Номер строки внутри блока (0, 1, 2…) |
| **Название** | Подпись слева: «Серия», «Память», «Материал» |
| **Источник из варианта** | Для Память/Цвет/SIM — выберите источник, поле «Значение» оставьте пустым |
| **Значение** | Текст или несколько строк (каждая строка — пункт списка на сайте) |

Пример: тип «Корпус», название «Материал», значение «алюминий».  
Несколько строк с одним **типом** автоматически объединяются в одну группу на сайте.

### Кнопка «Показать все / Свернуть»

API отдаёт **все** группы. Скрытие лишних групп — на фронте (например, первые 3 группы + кнопка).

### Отличие от `specifications`

- `specifications` — короткий flat-список для верха карточки (10–12 полей).
- `characteristicGroups` — полная таблица характеристик (десятки/сотни строк).

---

## 4. Объекты внутри `colors[]`

```json
{
  "id": 13,
  "name": "Green",
  "hex": "#34C759",
  "images": [
    {
      "id": "...",
      "url": "https://.../demo-apple-iphone-13-green-1.png",
      "alt": "Apple iPhone 13 — Green",
      "isPrimary": true,
      "sortOrder": 0,
      "colorId": 13,
      "color": { "id": 13, "name": "Green", "hex": "#34C759" }
    }
  ],
  "memories": [
    {
      "variantId": "abf93448-91ec-4856-8ca9-0a8dffa7a678",
      "memoryId": 1,
      "name": "128 GB",
      "price": 43500,
      "oldPrice": null,
      "discount": null,
      "isAvailable": true
    }
  ]
}
```

- **`hex`** — цвет кружка в пикере.
- **`images`** — фото только этого цвета (4+ штук).
- **`memories`** — доступные объёмы памяти для этого цвета.

---

## 5. Объект `selectedVariant`

```json
{
  "id": "563e81f3-43c7-4201-a32b-f48efc60c13f",
  "productId": 28,
  "memoryId": 1,
  "colorId": 2,
  "price": 43509.31,
  "oldPrice": null,
  "discount": null,
  "isAvailable": true,
  "images": [ "..." ],
  "memory": { "id": 1, "name": "128 GB" },
  "color": { "id": 2, "name": "Blue", "hex": "#2563EB" },
  "simType": { "id": "...", "name": "eSIM" },
  "simTypeId": "...",
  "simTypes": [
    {
      "simTypeId": "f74f962c-088a-4f27-b6c4-35f9bdb1a873",
      "price": 43615.12,
      "simType": { "id": "...", "name": "SIM+SIM" }
    }
  ],
  "specifications": [ { "key": "memory", "label": "Память", "value": "128 GB" } ]
}
```

### Что брать на UI

| Элемент | Поле |
|---------|------|
| Цена на кнопке «Купить» | `selectedVariant.price` (после выбора SIM — с `simTypeId` в query) |
| ID для корзины / избранного | `selectedVariant.id` (`variantId`) |
| Галерея слайдера | `images` (корневое) или `selectedVariant.images` |
| Характеристики | `specifications` |
| Блок SIM | `selectedVariant.simTypes` |

---

## 6. Сценарий работы страницы (пошагово)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Открытие /product/apple-iphone-13                        │
│    GET /api/product/slug/apple-iphone-13                    │
│    → рендер: colors[], images, selectedVariant, price       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Клик по цвету Green (id=13)                              │
│    GET .../apple-iphone-13?colorId=13                       │
│    → обновить галерею, selectedVariant, specifications      │
│    → подсветить активный цвет по selection.colorId          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Клик по памяти 128 GB (memoryId=1)                       │
│    GET ...?colorId=13&memoryId=1                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Клик по SIM+eSIM                                         │
│    GET ...?colorId=13&memoryId=1&simTypeId=6c9cfc6b-...     │
│    → price в selectedVariant меняется на цену из simTypes   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. «В корзину»                                              │
│    POST /api/cart  body: { variantId: selectedVariant.id }  │
└─────────────────────────────────────────────────────────────┘
```

### Важно

1. **Не фильтруйте** `variants[]` на клиенте для цены и картинок — делайте новый GET с query.
2. Без query сервер выбирает **первый** вариант в списке. Если это совпадает с `colorId=2`, ответ будет одинаковым — это нормально.
3. Для проверки фильтра используйте другой цвет, например `?colorId=13` (Green).
4. Массивы `colors[]` и `variants[]` **всегда полные** — для отображения всех опций в пикере.

---

## 7. Опционально: без повторного запроса

На первой загрузке в `colors[]` уже есть `images` и `memories` с ценами. Можно:

- **Вариант A (рекомендуется):** при каждом клике — новый GET с query (единый источник правды, актуальная цена с SIM).
- **Вариант B:** переключать галерею локально из `colors[n].images`, а запрос делать только при смене памяти/SIM или перед добавлением в корзину.

Если сомневаетесь — используйте **вариант A**.

---

## 8. URL в адресной строке (опционально)

Можно синхронизировать выбор с URL сайта:

```
/product/apple-iphone-13?colorId=13&memoryId=1
```

При загрузке страницы читайте query и передавайте те же параметры в API.

---

## 9. Связанные endpoints

| Действие | Метод и путь |
|----------|----------------|
| Похожие товары | `GET /api/product/slug/{slug}/related` |
| Trade-in заявка | `POST /api/product/trade-in-request` |
| Корзина | `GET/POST /api/cart` |
| Избранное | `GET/POST /api/favorites` |
| Поиск | `GET /api/product/search/{query}` |

### Trade-in — частая ошибка

Неверно (двойной `/api`):

```
POST /api/api/product/trade-in-request   ❌
```

Верно:

```
POST /api/product/trade-in-request   ✅
```

---

## 10. Категории и характеристики

Поле `specFields` зависит от категории (`category.slug`):

- `smartfony` — экран, диагональ, разрешение, частота, стекло, AOD и т.д.
- `pylesosy`, `naushniki` и др. — свой набор полей.

Показывайте только те строки из `specifications`, чьи `key` есть в `specFields` (+ всегда `memory` и `color` для варианта).

---

## 11. Чеклист для фронтенда

- [ ] Страница товара: `GET /api/product/slug/{slug}`
- [ ] Пикер цвета: данные из `colors[]`, активный — `selection.colorId`
- [ ] Пикер памяти: `colors[active].memories[]` или query `memoryId`
- [ ] Галерея: корневое `images` после каждого ответа API
- [ ] Цена: `selectedVariant.price`
- [ ] SIM: кнопки из `selectedVariant.simTypes`, при клике — `simTypeId` в query
- [ ] Корзина: `selectedVariant.id` как `variantId`
- [ ] Ошибка 400: показать сообщение, сбросить на дефолтный вариант
- [ ] Trade-in: `POST /api/product/trade-in-request` (без дубля `api`)

---

## 12. Демо-товар для тестов

| Поле | Значение |
|------|----------|
| Slug | `apple-iphone-13` |
| Цвета | Blue (2), Green (13), Starlight (14), Midnight (15) |
| Память | 128 GB (`memoryId: 1`) |

Проверка фильтра:

```bash
# Должны быть green-картинки и color.name = "Green"
curl "https://admin.geniusstorerf.ru/api/product/slug/apple-iphone-13?colorId=13"
```

---

## 13. TypeScript (пример типов)

```typescript
type ProductColor = {
  id: number;
  name: string;
  hex: string;
  images: ProductImage[];
  memories: {
    variantId: string;
    memoryId: number;
    name: string;
    price: number;
    oldPrice: number | null;
    discount: number | null;
    isAvailable: boolean;
  }[];
};

type ProductDetail = {
  id: number;
  title: string;
  slug: string;
  images: ProductImage[];
  colors: ProductColor[];
  specifications: { key: string; label: string; value: string }[];
  specFields: string[];
  selection: {
    colorId: number | null;
    memoryId: number | null;
    simTypeId: string | null;
  };
  selectedVariant: ProductVariant | null;
  variants: ProductVariant[];
};

async function fetchProduct(
  slug: string,
  params?: { colorId?: number; memoryId?: number; simTypeId?: string }
): Promise<ProductDetail> {
  const q = new URLSearchParams();
  if (params?.colorId != null) q.set('colorId', String(params.colorId));
  if (params?.memoryId != null) q.set('memoryId', String(params.memoryId));
  if (params?.simTypeId) q.set('simTypeId', params.simTypeId);

  const qs = q.toString();
  const url = `https://admin.geniusstorerf.ru/api/product/slug/${slug}${qs ? `?${qs}` : ''}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
```

---

*Документ актуален для API с поддержкой `colors[]`, `selectedVariant` и query-фильтра `colorId` / `memoryId` / `simTypeId`.*
