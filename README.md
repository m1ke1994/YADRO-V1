# TrackNode SaaS

## Описание проекта

TrackNode (`ydro`) — SaaS-платформа на Django и Vue для подключения сайтов,
сбора аналитики и лидов, SEO-аудита, PDF-отчётов, Telegram-уведомлений и
управления клиентскими данными.

Production-домен: `https://tracknode.ru`.

## Структура проекта

| Путь | Назначение |
| --- | --- |
| `config/` | Django settings, корневые URL и Celery |
| `apps/` | Основные приложения сайтов, аналитики, аккаунтов и media |
| `clients/`, `leads/` | Клиентский кабинет, настройки и заявки |
| `tracker/`, `analytics_app/` | Tracker API и агрегированная аналитика |
| `seo_audit/` | SEO-аудит, история, экспорт и AI-рекомендации |
| `reports/` | PDF-отчёты и периодические задачи |
| `subscriptions/` | Тарифы, подписки и YooKassa |
| `telegram_logs/` | Telegram webhook/polling и журнал обновлений |
| `vue-admin/` | Vue 3 + Vite SPA: кабинет и Vue Admin |
| `docker/backend/` | Backend entrypoint |
| `docker/nginx/` | Production Nginx, proxy и каталог сертификатов |
| `docker-compose.yml` | Локальная конфигурация |
| `docker-compose.prod.yml` | Production override |

Сервисы Docker: `postgres`, `redis`, `backend`, `celery_worker`,
`celery_beat`, `telegram_polling`, `frontend`, `nginx`.

## Переменные окружения

### Локальная разработка

Backend и локальный Docker Compose используют отслеживаемый Git файл
`.env.example`. Vue использует `vue-admin/.env.example`. В них находятся
только локальные тестовые значения.

Не добавляйте реальные токены и пароли в файлы `*.env.example`.

### Production

Production использует два неотслеживаемых файла:

- `.env` — Django, PostgreSQL, Redis, Celery, Telegram, billing и AI;
- `vue-admin/.env` — только публичные `VITE_*` значения frontend.

Оба файла исключены из Git и Docker build context. Значения `VITE_*`
попадают в браузерный bundle и не должны содержать секреты.

Минимальные обязательные значения `.env`:

```env
DJANGO_ENV=production
DJANGO_SECRET_KEY=replace-with-long-random-value
DJANGO_DEBUG=False
DJANGO_SERVE_MEDIA_FILES=False
DJANGO_ALLOWED_HOSTS=tracknode.ru,www.tracknode.ru,78.17.124.67
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
DJANGO_TRUST_X_FORWARDED_PROTO=True
DJANGO_USE_X_FORWARDED_HOST=True

DOMAIN=tracknode.ru
SITE_BASE_URL=https://tracknode.ru
PUBLIC_BASE_URL=https://tracknode.ru
FRONTEND_URL=https://tracknode.ru
API_URL=https://tracknode.ru/api
ADMIN_URL=https://tracknode.ru/admin

CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://tracknode.ru,https://www.tracknode.ru
CSRF_TRUSTED_ORIGINS=https://tracknode.ru,https://www.tracknode.ru

DB_ENGINE=postgres
POSTGRES_DB=tracknode
POSTGRES_USER=tracknode
POSTGRES_PASSWORD=replace-with-random-password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

Production `vue-admin/.env`:

```env
VITE_API_URL=https://tracknode.ru/api
VITE_BACKEND_URL=https://tracknode.ru
VITE_SITE_URL=https://tracknode.ru
VITE_SITE_NAME=TrackNode
VITE_SITE_DESCRIPTION=TrackNode объединяет аналитику сайтов, лиды, SEO-аудит и отчёты в одном кабинете.
VITE_FAVICON_URL=https://tracknode.ru/media/sites/a-meditation/frontend-assets/favicon.svg
VITE_OG_IMAGE_URL=https://tracknode.ru/media/sites/a-meditation/frontend-assets/og-image.svg
VITE_API_BASE_URL=https://tracknode.ru
```

Сгенерировать безопасные значения можно локально на сервере:

```bash
openssl rand -base64 48
openssl rand -base64 32
```

Первое значение используйте для `DJANGO_SECRET_KEY`, второе — для пароля
PostgreSQL. Не вставляйте результаты в Git, issue или логи.

## Локальный запуск

### Docker

```bash
docker compose --env-file .env.example config
docker compose --env-file .env.example up -d --build
docker compose --env-file .env.example ps
docker compose --env-file .env.example logs -f backend frontend
```

После запуска:

- Vue Admin: `http://localhost:8001`;
- API: `http://localhost:8000/api/`;
- healthcheck: `http://localhost:8000/api/health/`;
- Django Admin: `http://localhost:8000/admin/`.

Миграции и `collectstatic` выполняет backend entrypoint. При необходимости:

```bash
docker compose --env-file .env.example exec backend python manage.py migrate
docker compose --env-file .env.example exec backend python manage.py collectstatic --noinput
docker compose --env-file .env.example exec backend python manage.py createsuperuser
```

### Без Docker

Backend по умолчанию читает `.env.example` и использует SQLite:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd vue-admin
npm ci
npm run dev
```

Команда `npm run dev` использует Vite mode `example` и файл
`vue-admin/.env.example`.

## Production deploy на VPS

### 1. DNS и firewall

Создайте DNS `A`-записи `tracknode.ru` и `www.tracknode.ru`, указывающие на
`78.17.124.67`. На VPS откройте входящие TCP-порты `22`, `80`, `443`.
PostgreSQL, Redis, backend и Vite наружу не публикуются.

### 2. Установка Docker на Ubuntu

Актуальная официальная инструкция:
<https://docs.docker.com/engine/install/ubuntu/>.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME:-$VERSION_CODENAME} stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
newgrp docker
docker compose version
```

Нужен Docker Compose `2.24.4+`, потому что production override использует
тег `!override`.

### 3. Загрузка проекта

Через Git:

```bash
sudo mkdir -p /opt/tracknode
sudo chown "$USER":"$USER" /opt/tracknode
git clone <URL_РЕПОЗИТОРИЯ> /opt/tracknode/ydro
cd /opt/tracknode/ydro
```

Либо загрузите содержимое каталога `ydro/` в `/opt/tracknode/ydro` через
`rsync`/SFTP. Не загружайте локальные `.env`, базу, `media`, `node_modules`
и `vue-admin/dist`.

### 4. Настройка env

```bash
cd /opt/tracknode/ydro
cp .env.example .env
cp vue-admin/.env.example vue-admin/.env
nano .env
nano vue-admin/.env
chmod 600 .env vue-admin/.env
```

Замените локальные значения на production-настройки из раздела выше.
Обязательно заполните:

- `DJANGO_SECRET_KEY`;
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`;
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, если используется Telegram;
- `TELEGRAM_WEBHOOK_SECRET`, если выбран webhook;
- `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, если `ENABLE_BILLING=true`;
- `OPENAI_API_KEY`, если `AI_RECOMMENDATIONS_ENABLED=true`;
- все URL и origin для `https://tracknode.ru`.

### 5. TLS-сертификат

До первого запуска Nginx получите сертификат для обоих доменов. Standalone
режим требует свободный порт `80`:

```bash
sudo apt-get install -y certbot
sudo certbot certonly --standalone -d tracknode.ru -d www.tracknode.ru

sudo install -m 0644 /etc/letsencrypt/live/tracknode.ru/fullchain.pem docker/nginx/certs/fullchain.pem
sudo install -m 0600 /etc/letsencrypt/live/tracknode.ru/privkey.pem docker/nginx/certs/privkey.pem
```

После обновления сертификата повторите копирование файлов и выполните:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

Документация Certbot:
<https://eff-certbot.readthedocs.io/en/stable/using.html#standalone>.

### 6. Обязательный backup PostgreSQL

Перед `git pull`, пересборкой контейнеров, миграциями, изменением Compose,
PostgreSQL или production env обязательно создайте свежий дамп. Старые дампы
не удаляйте, пока новый deploy не проверен полностью.

Автоматическая команда:

```bash
cd /opt/tracknode/ydro
sh scripts/backup_postgres.sh
```

Дамп сохраняется локально на VPS:

```text
/opt/tracknode/ydro/backups/backup_YYYY-MM-DD_HH-MM-SS.sql
```

Каталог `backups/` исключён из Git. Скрипт сначала записывает временный файл,
проверяет, что он не пуст, и только затем переименовывает его в итоговый дамп.

Эквивалентная ручная команда:

```bash
cd /opt/tracknode/ydro
mkdir -p backups
BACKUP_FILE="backups/backup_$(date +%Y-%m-%d_%H-%M-%S).sql"

docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  exec -T postgres \
  sh -c 'pg_dump --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  > "$BACKUP_FILE"

test -s "$BACKUP_FILE" && ls -lh "$BACKUP_FILE"
```

Если команда завершилась с ошибкой или файл пуст, deploy продолжать нельзя.
Рекомендуется дополнительно скопировать дамп за пределы VPS в защищённое
хранилище.

#### Восстановление базы

Restore заменяет объекты и данные целевой базы содержимым дампа. Перед
восстановлением обязательно создайте ещё один свежий backup текущего
состояния и остановите сервисы, которые пишут в базу:

```bash
cd /opt/tracknode/ydro
sh scripts/backup_postgres.sh

docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  stop backend celery_worker celery_beat telegram_polling
```

Точная команда восстановления:

```bash
BACKUP_FILE="backups/backup_YYYY-MM-DD_HH-MM-SS.sql"

cat "$BACKUP_FILE" | docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  exec -T postgres \
  sh -c 'psql --single-transaction -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

После успешного восстановления:

```bash
docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up -d backend celery_worker celery_beat telegram_polling

docker compose \
  --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  exec backend python manage.py migrate --check
```

Без свежего проверенного дампа запрещено выполнять `migrate`, restore,
удаление/recreate PostgreSQL container или volume, `docker compose down -v`,
смену схемы/моделей, массовое изменение данных и замену production `.env`.

### 7. Проверка и запуск

```bash
cd /opt/tracknode/ydro

docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml config
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml build
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml up -d

docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py createsuperuser

docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml logs -f nginx backend frontend celery_worker celery_beat
```

Для первого запуска пустой базы предварительный дамп не требуется. Для
повторного deploy существующей установки перед `build`, `up` и `migrate`
обязательно выполните `sh scripts/backup_postgres.sh`.

Backend entrypoint также автоматически выполняет миграции и
`collectstatic`; повторный ручной запуск безопасен и удобен для контроля.

## Nginx

Production Nginx находится в
`docker/nginx/templates/default.conf.template` и является единственной
публичной точкой входа:

| Маршрут | Обработчик |
| --- | --- |
| `/api/` | Django/Gunicorn |
| `/admin/` | Django Admin |
| `/tracker.js` | Генерируемый Django tracker |
| `/static/` | volume `static_data` |
| `/media/` | volume `media_data` |
| `/assets/` | собранные Vite assets |
| `/robots.txt` | frontend public-файл |
| `/sitemap.xml` | frontend public-файл |
| остальные маршруты | Vue SPA через `index.html` |

HTTP перенаправляется на HTTPS. `www.tracknode.ru` перенаправляется на
`tracknode.ru`. Proxy передаёт Django заголовки `Host`,
`X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto`.

## Эндпоинты API

Для JWT-запросов используйте заголовок:

```text
Authorization: Bearer <access_token>
```

Для публичного tracker API используется API key сайта согласно интеграционному
скрипту. Основные маршруты:

| Метод | Путь | Назначение | Авторизация |
| --- | --- | --- | --- |
| GET | `/api/` | Карта API | Нет |
| GET | `/api/health/` | Healthcheck | Нет |
| POST | `/api/auth/token/` | Получить JWT | Нет |
| POST | `/api/auth/token/refresh/` | Обновить JWT | Refresh token |
| GET | `/api/auth/me/` | Текущий пользователь | JWT |
| POST | `/api/mini/auth/register/` | Регистрация клиента | Нет |
| POST | `/api/mini/auth/login/` | Вход Mini API | Нет |
| POST | `/api/mini/auth/logout/` | Выход | JWT |
| POST | `/api/mini/auth/change-password/` | Смена пароля | JWT |
| GET | `/api/public/sites/<slug>/` | Публичные данные сайта | Нет |
| GET | `/api/public/sites/<slug>/sections/` | Разделы сайта | Нет |
| GET | `/api/public/sites/<slug>/sections/<key>/` | Раздел сайта | Нет |
| GET | `/api/public/by-domain/?domain=...` | Сайт по домену | Нет |
| POST | `/api/public/sites/<slug>/leads/` | Создать заявку | Нет |
| POST | `/api/leads/` | Создать заявку, совместимый endpoint | Нет |
| GET | `/api/admin/my-sites/` | Сайты пользователя | JWT |
| GET | `/api/admin/my-sites/<id>/` | Данные сайта | JWT |
| GET, POST | `/api/admin/my-sites/<id>/sections/` | Список/создание раздела | JWT |
| GET, PATCH, DELETE | `/api/admin/my-sites/<id>/sections/<id>/` | Раздел сайта | JWT |
| GET | `/api/admin/leads/` | Список заявок | JWT |
| GET, PATCH | `/api/admin/leads/<id>/` | Заявка и её статус | JWT |
| GET | `/api/admin/my-sites/<id>/analytics/summary/` | Аналитика сайта | JWT |
| POST | `/api/admin/my-sites/<id>/tracking-key/refresh/` | Новый API key | JWT |
| GET | `/api/admin/my-sites/<id>/telegram/` | Статус Telegram | JWT |
| POST | `/api/admin/my-sites/<id>/telegram/test/` | Тест Telegram | JWT |
| POST | `/api/admin/my-sites/<id>/telegram/disconnect/` | Отключить Telegram | JWT |
| POST | `/api/track/visit-start/` | Начало визита | API key |
| POST | `/api/track/pageview/` | Просмотр страницы | API key |
| POST | `/api/track/event/` | Событие | API key |
| POST | `/api/track/visit-end/` | Завершение визита | API key |
| GET | `/api/track/stats/` | Статистика tracker | API key |
| POST | `/api/public/event/` | Публичное событие | API key |
| POST | `/api/analytics/event/` | Аналитическое событие | API key |
| GET | `/api/analytics/overview/` | Обзор аналитики | JWT + подписка |
| GET | `/api/analytics/engagement/` | Вовлечённость | JWT + подписка |
| GET | `/api/analytics/devices/` | Устройства/браузеры/ОС | JWT + подписка |
| GET | `/api/analytics/unique-daily/` | Уникальные посетители | JWT + подписка |
| GET | `/api/analytics/summary/` | Сводный отчёт | JWT + подписка |
| GET | `/api/analytics/ai-recommendations/` | AI-рекомендации | JWT + подписка |
| POST | `/api/seo/start/` | Запустить SEO-аудит | JWT + подписка |
| GET | `/api/seo/latest/` | Последний аудит | JWT + подписка |
| GET | `/api/seo/audits/` | Список аудитов | JWT + подписка |
| GET | `/api/seo/<id>/` | Детали аудита | JWT + подписка |
| POST | `/api/seo/<id>/stop/` | Остановить аудит | JWT + подписка |
| GET | `/api/seo/<id>/pages/` | Проверенные страницы | JWT + подписка |
| GET | `/api/seo/<id>/issues/` | SEO-проблемы | JWT + подписка |
| GET | `/api/seo/<id>/history/` | История | JWT + подписка |
| GET | `/api/seo/<id>/compare/` | Сравнение | JWT + подписка |
| GET | `/api/seo/<id>/ai-recommendations/` | SEO AI-рекомендации | JWT + подписка |
| GET | `/api/seo/<id>/export/` | Экспорт аудита | JWT + подписка |
| POST | `/api/reports/send-now/` | Создать/отправить PDF | JWT + подписка |
| GET, POST | `/api/reports/toggle-daily/` | Статус/переключение отчётов | JWT + подписка |
| GET | `/api/subscription/status/` | Статус подписки | JWT |
| GET | `/api/subscription/plans/` | Тарифы | Нет |
| POST | `/api/subscription/create-payment/` | Создать платёж | JWT |
| POST | `/api/subscription/webhook/` | Billing webhook | Провайдер |
| GET, PATCH | `/api/settings/` | Настройки клиента | JWT |
| GET | `/api/client/media/` | Список/поиск media | JWT |
| POST | `/api/client/media/upload/` | Загрузка media | JWT |
| GET, PATCH, DELETE | `/api/client/media/<id>/` | Просмотр, метаданные, удаление media | JWT |
| POST | `/api/uploads/` | Совместимый upload endpoint | JWT |
| POST | `/api/public/telegram/webhook/` | Telegram webhook | Secret header |

Маршруты `/api/mini/...` сохраняют совместимые aliases для tracker,
аналитики, SEO, reports, subscription, settings, leads и Telegram.

Пример получения JWT:

```bash
curl -X POST https://tracknode.ru/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@example.com","password":"change-me"}'
```

Пример заявки:

```bash
curl -X POST https://tracknode.ru/api/leads/ \
  -H "Content-Type: application/json" \
  -d '{"site_slug":"demo","name":"Иван","phone":"+79990000000","message":"Тестовая заявка"}'
```

Успешный ответ заявки:

```json
{"success": true, "message": "Заявка успешно отправлена"}
```

## Работа с медиафайлами

Изображения сайтов хранятся в Django `MEDIA_ROOT` и production volume
`media_data`. Стандартная структура:

```text
media/
└── sites/
    └── <site-slug>/
        ├── hero/
        ├── gallery/
        ├── reviews/
        ├── uploads/
        └── frontend-assets/
```

Каждому управляемому файлу соответствует запись `MediaFile`: сайт, секция,
исходное имя, размер, MIME type, SHA-256, title, alt-текст, пользователь и
дата загрузки. Полный аудит и карта старых URL находятся в
`docs/images_audit.md`.

### Media Library в Vue Admin

Для image/media-полей доступны загрузка, preview, выбор существующего файла,
замена, редактирование title/alt-текста и удаление из Media Library.

Кнопка удаления в редакторе секции очищает только значение поля. Физическое
удаление из Media Library выполняется отдельно и может затронуть другие
секции, если они используют тот же URL.

API поиска:

```text
GET /api/client/media/?site=<id-or-slug>&file_type=image&search=<text>
```

### Массовый импорт

Команда сканирует проект, исключая dependencies, build output, backup и
Python environments. Поддерживаются `jpg`, `jpeg`, `png`, `webp`, `svg`,
`gif`, `avif`.

Перед production-импортом обязателен backup:

```bash
cd /opt/tracknode/ydro
sh scripts/backup_postgres.sh
```

Dry-run:

```bash
docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  exec backend python manage.py import_site_media \
  --site a-meditation \
  --dry-run
```

Импорт:

```bash
docker compose --env-file .env \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  exec backend python manage.py import_site_media \
  --site a-meditation
```

Отчёт создаётся в `docs/media_import_report_YYYY-MM-DD_HH-MM-SS.md` и
содержит количество найденных, импортированных, пропущенных и дублирующихся
файлов, общий объём и карту `исходный путь -> media URL`.

Команда идемпотентна по SHA-256 в рамках сайта. Исходные файлы, существующие
записи и старые данные автоматически не удаляются.

## Telegram

Нужные переменные:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_USERNAME=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_USE_WEBHOOK=false
TELEGRAM_BIND_TOKEN_MAX_AGE=3600
```

По умолчанию контейнер `telegram_polling` использует long polling. При
`TELEGRAM_USE_WEBHOOK=true` polling завершается, а обновления принимает:

```text
https://tracknode.ru/api/public/telegram/webhook/
```

Webhook Telegram должен передавать `TELEGRAM_WEBHOOK_SECRET` в заголовке
`X-Telegram-Bot-Api-Secret-Token`.

Проверка:

1. Заполнить токен и username бота.
2. Перезапустить `backend` и `telegram_polling`.
3. В кабинете сайта нажать подключение Telegram и отправить боту `/start`.
4. Вызвать кнопку тестового сообщения.
5. Создать тестовую заявку и проверить сообщение и логи.

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml logs -f telegram_polling backend
```

## SEO

SEO-файлы frontend:

- `vue-admin/public/robots.txt`;
- `vue-admin/public/sitemap.xml`;
- `vue-admin/public/favicon.svg`;
- `vue-admin/public/og-image.svg`;
- meta-теги в `vue-admin/index.html`;
- route-level title/canonical/robots в `vue-admin/src/config/seo.js`.

Корень приложения получает базовые `title`, `description`, canonical,
Open Graph и Twitter Card. Авторизованные маршруты и форма входа получают
`noindex,nofollow`, поскольку это приватный кабинет, а не публичный контент.

После деплоя:

```bash
curl -I https://tracknode.ru/robots.txt
curl -I https://tracknode.ru/sitemap.xml
curl -I https://tracknode.ru/media/sites/a-meditation/frontend-assets/favicon.svg
curl -I https://tracknode.ru/media/sites/a-meditation/frontend-assets/og-image.svg
curl -s https://tracknode.ru/ | grep -E "canonical|og:|description"
```

Vite формирует статический HTML. Для индексируемого публичного маркетингового
сайта с уникальными meta на каждой странице потребуется SSR/prerender,
но для текущего приватного SPA это не требуется.

## SPA

Vue использует `createWebHistory()`. Nginx проверяет существующий файл и
для остальных frontend URL возвращает `/index.html`:

```nginx
try_files $uri $uri/ /index.html;
```

Поэтому обновление `/dashboard`, `/sites/1/analytics`, `/mini/reports` и
других Vue-маршрутов не должно давать 404. `/api/`, `/admin/`, `/static/`,
`/media/`, `/tracker.js`, SEO-файлы и Vite assets обрабатываются до fallback.

Проверка без авторизации должна вернуть SPA, после чего Vue перенаправит на
`/login`:

```bash
curl -I https://tracknode.ru/some-route
curl -I https://tracknode.ru/dashboard
```

## Полезные команды

Локально:

```bash
docker compose --env-file .env.example up -d --build
docker compose --env-file .env.example logs -f
docker compose --env-file .env.example exec backend python manage.py migrate
docker compose --env-file .env.example exec backend python manage.py collectstatic --noinput
docker compose --env-file .env.example exec backend python manage.py createsuperuser
docker compose --env-file .env.example restart
docker compose --env-file .env.example down
```

Production:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml logs -f
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py createsuperuser
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml restart
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml down
```

Обновление:

```bash
cd /opt/tracknode/ydro
sh scripts/backup_postgres.sh
git pull --ff-only
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml config
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml ps
```

## Проверка после деплоя

```bash
curl -I https://tracknode.ru/
curl -I https://www.tracknode.ru/
curl -I https://tracknode.ru/dashboard
curl -I https://tracknode.ru/admin/
curl -I https://tracknode.ru/static/admin/css/base.css
curl -I https://tracknode.ru/robots.txt
curl -I https://tracknode.ru/sitemap.xml
curl -I https://tracknode.ru/tracker.js
curl https://tracknode.ru/api/health/
```

Дополнительно вручную проверить:

- регистрацию, вход, refresh token и выход;
- Django Admin и Vue Admin;
- создание/редактирование разделов сайта;
- загрузку и открытие media;
- tracker.js, визиты, pageview и события;
- аналитику и multi-tenant изоляцию;
- создание и смену статуса заявки;
- Telegram-подключение, тест и уведомление о заявке;
- запуск SEO-аудита и экспорт;
- генерацию PDF-отчёта;
- платежи только после заполнения production-ключей YooKassa.
