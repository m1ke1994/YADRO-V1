# Vue Admin

Клиентская админка Mini CRM на Vue 3 и Vite.

## Локальный запуск

```bash
npm ci
npm run dev
```

Админка откроется на `http://localhost:5173`. Команда использует
`vue-admin/.env.example`.

Переменные:

- `VITE_API_URL` — API с префиксом `/api`
- `VITE_BACKEND_URL` — origin backend для media и абсолютных URL
- `VITE_SITE_URL` — публичный URL frontend
- `VITE_API_BASE_URL` — совместимый alias старой конфигурации

Production-сборка использует `vue-admin/.env`:

```bash
npm run build
```

Production-значения для TrackNode:

```env
VITE_API_URL=https://tracknode.ru/api
VITE_BACKEND_URL=https://tracknode.ru
VITE_SITE_URL=https://tracknode.ru
```

Локальная проверка сборки:

```bash
npm run build:local
```

## Docker

Запуск backend и Vue Admin:

```bash
docker compose --env-file .env.example up --build -d backend frontend
```

После запуска:

- Vue Admin: `http://localhost:8001`
- Backend API: `http://localhost:8000`

Для разработки каталог `vue-admin` подключён в контейнер как bind mount.
Изменения подхватываются Vite автоматически.

Полная пересборка frontend:

```bash
docker compose build --no-cache frontend
docker compose up -d frontend
```

Проверка конфигурации:

```bash
docker compose --env-file .env.example config
```

## Проверка

```bash
npm run build
```

Проверьте адаптивность в инструментах разработчика браузера на ширинах
1440 px, 768 px и 390 px.
