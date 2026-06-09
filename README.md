# TrackNode SaaS

Django backend, Vue Admin, PostgreSQL, Redis, Celery и Telegram-интеграция.

## Окружения

- Локальная разработка использует безопасный шаблон `.env.example`.
- Production использует локальный, не отслеживаемый Git файл `.env`.
- Vue Admin локально использует `vue-admin/.env.example`.
- Vue Admin при production-сборке использует `vue-admin/.env`.

Не копируйте production-секреты в `.env.example`.

## Локальный запуск Docker

```bash
docker compose --env-file .env.example up --build
```

После запуска:

- Backend API: `http://localhost:8000`
- Vue Admin: `http://localhost:8001`

Если порты заняты, задайте перед запуском `BACKEND_PORT`, `FRONTEND_PORT` и
`PUBLIC_SITE_PORT`. При изменении backend-порта также обновите локальные
`VITE_API_URL` и `VITE_BACKEND_URL`.

Миграции и сборка static выполняются backend entrypoint автоматически.

Внешний demo frontend ожидается в `../a-meditation/frontend` и вынесен в
опциональный profile:

```bash
docker compose --env-file .env.example --profile public-site up --build
```

## Локальный запуск без Docker

Backend по умолчанию читает `.env.example`, где используется SQLite:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Vue Admin:

```bash
cd vue-admin
npm ci
npm run dev
```

Команда `npm run dev` запускает Vite с mode `example`, поэтому локальные
значения берутся из `vue-admin/.env.example`, даже если рядом существует
production-файл `.env`.

## Production

Перед запуском заполните `.env` и `vue-admin/.env`. Эти файлы остаются только
на production-хосте и не должны попадать в Git или Docker build context.

Production использует единую публичную схему:

- сайт и Vue Admin: `https://tracknode.ru`
- API: `https://tracknode.ru/api`
- Django Admin: `https://tracknode.ru/admin`
- tracker: `https://tracknode.ru/tracker.js`
- `https://www.tracknode.ru` перенаправляется на основной домен

DNS-записи `tracknode.ru` и `www.tracknode.ru` должны указывать на production-сервер.
TLS-сертификат должен покрывать оба имени. Разместите сертификаты:

```text
docker/nginx/certs/fullchain.pem
docker/nginx/certs/privkey.pem
```

Сертификаты игнорируются Git. Nginx является единственной публичной точкой
входа; backend и frontend напрямую на host-порты в production не публикуются.

Проверка итоговой конфигурации:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml config
```

Запуск:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Production override требует Docker Compose 2.24.4 или новее из-за тега
`!override`.

Для запуска Django без Docker укажите production env-файл явно:

```powershell
$env:DJANGO_ENV_FILE=".env"
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

Production-сборка Vue Admin:

```bash
cd vue-admin
npm ci
npm run build
```

Для проверки локальной frontend-сборки без production-конфигурации:

```bash
npm run build:local
```

## Обязательные production-настройки

Проверьте в `.env`:

- `DJANGO_ENV=production`
- `DOMAIN=tracknode.ru`
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=tracknode.ru,www.tracknode.ru`
- `DJANGO_SECURE_SSL_REDIRECT`, secure cookie и HSTS-флаги
- `DATABASE_URL` или набор `POSTGRES_*`
- `REDIS_URL`
- `CORS_ALLOW_ALL_ORIGINS=False`
- `CORS_ALLOWED_ORIGINS=https://tracknode.ru,https://www.tracknode.ru`
- `CSRF_TRUSTED_ORIGINS=https://tracknode.ru,https://www.tracknode.ru`
- `SITE_BASE_URL=https://tracknode.ru`
- `PUBLIC_BASE_URL=https://tracknode.ru`
- `FRONTEND_URL=https://tracknode.ru`
- `API_URL=https://tracknode.ru/api`
- `ADMIN_URL=https://tracknode.ru/admin`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`
- `TELEGRAM_WEBHOOK_SECRET`, если используется webhook
- `YOOKASSA_*`, если включен billing
- `OPENAI_API_KEY`, если включены AI-рекомендации

Проверьте в `vue-admin/.env`:

```env
VITE_API_URL=https://tracknode.ru/api
VITE_BACKEND_URL=https://tracknode.ru
VITE_SITE_URL=https://tracknode.ru
```

Все значения `VITE_*` являются публичными и попадают в frontend bundle.

`VITE_API_BASE_URL` сохранен как временный совместимый alias для старых
окружений. Новая конфигурация использует `VITE_API_URL` и
`VITE_BACKEND_URL`.

## Проверки

```bash
python manage.py check
python manage.py migrate --check
python manage.py test
cd vue-admin
npm run build:local
```

Docker:

```bash
docker compose config
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml config
```

Проверка состояния production:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose --env-file .env -f docker-compose.yml -f docker-compose.prod.yml logs nginx backend frontend
curl https://tracknode.ru/api/health/
```

## Tracker и Telegram

Tracker доступен по `GET /tracker.js` и `GET /api/mini/tracker.js`.
Публичный URL формируется из `PUBLIC_BASE_URL`.

Telegram использует настройки из окружения:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `TELEGRAM_BOT_USERNAME`
- `TELEGRAM_USE_WEBHOOK`
- `TELEGRAM_BIND_TOKEN_MAX_AGE`
