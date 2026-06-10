# Аудит изображений TrackNode / Ядро

Дата аудита: 10 июня 2026 года.

## Методика

Просканированы расширения `jpg`, `jpeg`, `png`, `webp`, `svg`, `gif`,
`avif` во всём репозитории. Из отчёта исключены `.git`, `node_modules`,
`dist`, `staticfiles`, `venv`, `env`, `__pycache__` и `backups`: это
зависимости, результаты сборки или резервные копии, а не исходные изображения
проекта.

Использование проверено в Python, Vue, JavaScript, CSS/SCSS, HTML, JSON,
YAML, env-шаблонах, конфигурациях секций и локальной базе Django.

## Итоги

- Файлов изображений: **32**.
- Уникальных изображений по SHA-256: **18**.
- Общий физический объём: **25 186 999 байт** (около 24,02 MiB).
- Файлов, входящих в группы дубликатов: **26**.
- Лишних физических копий относительно уникальных файлов: **14**.
- Runtime-записей изображений `MediaFile` в локальной БД: **14**.
- Неиспользуемых frontend starter-файлов: **4**.
- Изображений WebP/GIF/AVIF в текущем репозитории не найдено.

`demo_public/images/` содержит исходники для seed. Каталог
`media/sites/a-meditation/` содержит их runtime-копии, уже связанные с
секциями сайта через `MediaFile` и JSON `SiteSection.content`.

## Полный список

| Путь | Размер, байт | Тип | Где используется | Использований |
| --- | ---: | --- | --- | ---: |
| `demo_public/images/2025-02-26 12-35-42.JPG` | 473363 | JPG | Seed: `about`, `guide` | 4 |
| `demo_public/images/2025-02-26 13-06-17.JPG` | 99691 | JPG | Seed: `gallery.items[1]` | 2 |
| `demo_public/images/DSC08101.JPG` | 9502720 | JPG | Seed: `gallery.items[0]` | 3 |
| `demo_public/images/IMG_1245.JPG` | 348735 | JPG | Seed: `reviews.items[0].avatar` | 3 |
| `demo_public/images/IMG_1246.JPG` | 286692 | JPG | Seed: `reviews.items[1].avatar` | 3 |
| `demo_public/images/IMG_1249.JPG` | 354325 | JPG | Seed: `reviews.items[2].avatar` | 2 |
| `demo_public/images/IMG_1988.JPG` | 278529 | JPG | Seed: `reviews.items[3].avatar` | 2 |
| `demo_public/images/IMG_5131.JPG` | 244071 | JPG | Seed: `gallery.items[2]` | 3 |
| `demo_public/images/Lila_Olga_2.2.poster.jpg` | 256018 | JPG | Seed: `hero.image`, `gallery.items[3]` | 5 |
| `demo_public/images/m1.jpg` | 125283 | JPG | Seed: `meditations.items[0].image` | 3 |
| `demo_public/images/m3.jpg` | 115653 | JPG | Seed: `meditations.items[2].image` | 3 |
| `demo_public/images/m4.jpg` | 124946 | JPG | Seed: `meditations.items[3].image` | 2 |
| `media/sites/a-meditation/about/2025-02-26 12-35-42.JPG` | 473363 | JPG | Runtime: секция `about`, поле `image` | 1 |
| `media/sites/a-meditation/gallery/2025-02-26 13-06-17.JPG` | 99691 | JPG | Runtime: `gallery.items.1.src` | 1 |
| `media/sites/a-meditation/gallery/DSC08101.JPG` | 9502720 | JPG | Runtime: `gallery.items.0.src` | 1 |
| `media/sites/a-meditation/gallery/IMG_5131.JPG` | 244071 | JPG | Runtime: `gallery.items.2.src` | 1 |
| `media/sites/a-meditation/gallery/Lila_Olga_2.2.poster.jpg` | 256018 | JPG | Runtime: `gallery.items.3.src` | 1 |
| `media/sites/a-meditation/guide/2025-02-26 12-35-42.JPG` | 473363 | JPG | Runtime: секция `guide`, поле `image` | 1 |
| `media/sites/a-meditation/hero/Lila_Olga_2.2.poster.jpg` | 256018 | JPG | Runtime: секция `hero`, поле `image` | 1 |
| `media/sites/a-meditation/meditations/m1.jpg` | 125283 | JPG | Runtime: `meditations.items.0.image` | 1 |
| `media/sites/a-meditation/meditations/m3.jpg` | 115653 | JPG | Runtime: `meditations.items.2.image` | 1 |
| `media/sites/a-meditation/meditations/m4.jpg` | 124946 | JPG | Runtime: `meditations.items.3.image` | 1 |
| `media/sites/a-meditation/reviews/IMG_1245.JPG` | 348735 | JPG | Runtime: `reviews.items.0.avatar` | 1 |
| `media/sites/a-meditation/reviews/IMG_1246.JPG` | 286692 | JPG | Runtime: `reviews.items.1.avatar` | 1 |
| `media/sites/a-meditation/reviews/IMG_1249.JPG` | 354325 | JPG | Runtime: `reviews.items.2.avatar` | 1 |
| `media/sites/a-meditation/reviews/IMG_1988.JPG` | 278529 | JPG | Runtime: `reviews.items.3.avatar` | 1 |
| `vue-admin/public/favicon.svg` | 9522 | SVG | `vue-admin/index.html`, favicon | 1 |
| `vue-admin/public/icons.svg` | 5031 | SVG | Текстовых использований не найдено | 0 |
| `vue-admin/public/og-image.svg` | 751 | SVG | SEO env и `src/config/seo.js` | 3 |
| `vue-admin/src/assets/hero.png` | 13057 | PNG | Использований не найдено | 0 |
| `vue-admin/src/assets/vite.svg` | 8709 | SVG | Использований не найдено | 0 |
| `vue-admin/src/assets/vue.svg` | 496 | SVG | Использований не найдено | 0 |

## Используемые изображения

Используются все 12 файлов `demo_public/images/`: это исходники для
`seed_demo_data`. Их runtime-копии используются секциями:

- `hero`: `Lila_Olga_2.2.poster.jpg`;
- `about` и `guide`: `2025-02-26 12-35-42.JPG`;
- `meditations`: `m1.jpg`, `m3.jpg`, `m4.jpg`;
- `gallery`: `DSC08101.JPG`, `2025-02-26 13-06-17.JPG`, `IMG_5131.JPG`,
  `Lila_Olga_2.2.poster.jpg`;
- `reviews`: `IMG_1245.JPG`, `IMG_1246.JPG`, `IMG_1249.JPG`, `IMG_1988.JPG`.

Во frontend используются `favicon.svg` и `og-image.svg`. В local окружении
они доступны из `public/`. В production переменные `VITE_FAVICON_URL` и
`VITE_OG_IMAGE_URL` указывают на импортированные копии в Django media.
Исходные public-файлы не удаляются: они нужны как источник импорта и
безопасный локальный fallback.

## Неиспользуемые изображения

- `vue-admin/public/icons.svg`;
- `vue-admin/src/assets/hero.png`;
- `vue-admin/src/assets/vite.svg`;
- `vue-admin/src/assets/vue.svg`.

Они готовы к импорту и учёту, но автоматически не удаляются.

## Дубликаты

Дубликаты определены по SHA-256, а не по имени:

- `2025-02-26 12-35-42.JPG`: source + `about` + `guide`;
- `Lila_Olga_2.2.poster.jpg`: source + `hero` + `gallery`;
- остальные десять demo-изображений имеют по одной runtime-копии.

Management command не создаёт новые записи для одинакового SHA-256 в рамках
одного сайта. Уже существующие context-specific записи не удаляются, чтобы
не ломать текущие URL секций.

## Карта миграции

| Старый путь | Текущий/целевой media URL |
| --- | --- |
| `/images/2025-02-26 12-35-42.JPG` | `/media/sites/a-meditation/about/2025-02-26%2012-35-42.JPG` |
| `/images/2025-02-26 13-06-17.JPG` | `/media/sites/a-meditation/gallery/2025-02-26%2013-06-17.JPG` |
| `/images/DSC08101.JPG` | `/media/sites/a-meditation/gallery/DSC08101.JPG` |
| `/images/IMG_1245.JPG` | `/media/sites/a-meditation/reviews/IMG_1245.JPG` |
| `/images/IMG_1246.JPG` | `/media/sites/a-meditation/reviews/IMG_1246.JPG` |
| `/images/IMG_1249.JPG` | `/media/sites/a-meditation/reviews/IMG_1249.JPG` |
| `/images/IMG_1988.JPG` | `/media/sites/a-meditation/reviews/IMG_1988.JPG` |
| `/images/IMG_5131.JPG` | `/media/sites/a-meditation/gallery/IMG_5131.JPG` |
| `/images/Lila_Olga_2.2.poster.jpg` | `/media/sites/a-meditation/hero/Lila_Olga_2.2.poster.jpg` |
| `/images/m1.jpg` | `/media/sites/a-meditation/meditations/m1.jpg` |
| `/images/m3.jpg` | `/media/sites/a-meditation/meditations/m3.jpg` |
| `/images/m4.jpg` | `/media/sites/a-meditation/meditations/m4.jpg` |
| `vue-admin/public/favicon.svg` | `/media/sites/<site>/frontend-assets/favicon.svg` |
| `vue-admin/public/icons.svg` | `/media/sites/<site>/frontend-assets/icons.svg` |
| `vue-admin/public/og-image.svg` | `/media/sites/<site>/frontend-assets/og-image.svg` |
| `vue-admin/src/assets/hero.png` | `/media/sites/<site>/frontend-assets/hero.png` |
| `vue-admin/src/assets/vite.svg` | `/media/sites/<site>/frontend-assets/vite.svg` |
| `vue-admin/src/assets/vue.svg` | `/media/sites/<site>/frontend-assets/vue.svg` |

Точный итоговый URL для новых файлов фиксируется в отчёте команды
`import_site_media`; Django нормализует имена через `_build_upload_path`.

## Команда импорта

Dry-run:

```bash
python manage.py import_site_media --site a-meditation --dry-run
```

Импорт:

```bash
python manage.py import_site_media --site a-meditation
```

Перед production-импортом обязателен PostgreSQL backup:

```bash
sh scripts/backup_postgres.sh
```
