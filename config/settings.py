from datetime import timedelta
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = Path(os.getenv("DJANGO_ENV_FILE", ".env.example"))
if not ENV_FILE.is_absolute():
    ENV_FILE = BASE_DIR / ENV_FILE
load_dotenv(ENV_FILE, override=False)


def env(key, default=None, aliases=()):
    for candidate in (key, *aliases):
        value = os.getenv(candidate)
        if value not in (None, ""):
            return value
    return default


def env_bool(key, default=False, aliases=()):
    return str(env(key, default, aliases=aliases)).lower() in {"1", "true", "yes", "on"}


def env_csv(key, default="", aliases=()):
    return [item.strip() for item in str(env(key, default, aliases=aliases)).split(",") if item.strip()]


DJANGO_ENV = env("DJANGO_ENV", "development").strip().lower()
IS_PRODUCTION = DJANGO_ENV == "production"


def required_env(key, aliases=()):
    value = env(key, aliases=aliases)
    if value in (None, ""):
        raise ImproperlyConfigured(f"{key} must be set when DJANGO_ENV=production")
    return value


def public_url(key, default="", aliases=()):
    value = env(key, default, aliases=aliases).rstrip("/")
    if not IS_PRODUCTION:
        return value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ImproperlyConfigured(f"{key} must be an absolute HTTP(S) URL in production")
    if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
        raise ImproperlyConfigured(f"{key} cannot use a local address in production")
    if REQUIRE_HTTPS and parsed.scheme != "https":
        raise ImproperlyConfigured(f"{key} must use HTTPS when DJANGO_REQUIRE_HTTPS=true")
    return value


SECRET_KEY = (
    required_env("DJANGO_SECRET_KEY", aliases=("SECRET_KEY",))
    if IS_PRODUCTION
    else env("DJANGO_SECRET_KEY", "local-development-only", aliases=("SECRET_KEY",))
)
DEBUG = env_bool("DJANGO_DEBUG", not IS_PRODUCTION)
REQUIRE_HTTPS = env_bool("DJANGO_REQUIRE_HTTPS", IS_PRODUCTION)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", IS_PRODUCTION)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", IS_PRODUCTION)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", IS_PRODUCTION)
SECURE_HSTS_SECONDS = int(env("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)
if env_bool("DJANGO_TRUST_X_FORWARDED_PROTO", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env_bool("DJANGO_USE_X_FORWARDED_HOST", IS_PRODUCTION)

DEFAULT_ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver", "backend"]
ALLOWED_HOSTS = env_csv(
    "DJANGO_ALLOWED_HOSTS",
    "" if IS_PRODUCTION else ",".join(DEFAULT_ALLOWED_HOSTS),
    aliases=("ALLOWED_HOSTS",),
)
if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS must be set when DJANGO_ENV=production")
if IS_PRODUCTION and any(host in {"localhost", "127.0.0.1", "0.0.0.0"} for host in ALLOWED_HOSTS):
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS cannot contain local addresses in production")

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "rest_framework",
    "apps.accounts",
    "apps.analytics",
    "apps.sites",
    "apps.mediafiles",
    "clients",
    "leads",
    "analytics_app",
    "tracker",
    "seo_audit",
    "reports",
    "subscriptions",
    "telegram_logs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = env("DATABASE_URL", "").strip()
DB_ENGINE = env("DB_ENGINE", "sqlite").lower()
if DATABASE_URL:
    parsed_database_url = urlparse(DATABASE_URL)
    if parsed_database_url.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("DATABASE_URL must use postgres:// or postgresql://")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed_database_url.path.lstrip("/")),
            "USER": unquote(parsed_database_url.username or ""),
            "PASSWORD": unquote(parsed_database_url.password or ""),
            "HOST": parsed_database_url.hostname or "",
            "PORT": str(parsed_database_url.port or 5432),
        }
    }
elif DB_ENGINE == "postgres":
    postgres_defaults = {
        "POSTGRES_DB": None if IS_PRODUCTION else "django_db",
        "POSTGRES_USER": None if IS_PRODUCTION else "postgres",
        "POSTGRES_PASSWORD": None if IS_PRODUCTION else "postgres",
        "POSTGRES_HOST": None if IS_PRODUCTION else "localhost",
        "POSTGRES_PORT": "5432",
    }
    postgres_values = {
        key: env(key, default, aliases=(key.replace("POSTGRES_", "DB_"),))
        for key, default in postgres_defaults.items()
    }
    missing_postgres_values = [key for key, value in postgres_values.items() if not value]
    if missing_postgres_values:
        raise ImproperlyConfigured(
            f"{', '.join(missing_postgres_values)} must be set when DB_ENGINE=postgres"
        )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": postgres_values["POSTGRES_DB"],
            "USER": postgres_values["POSTGRES_USER"],
            "PASSWORD": postgres_values["POSTGRES_PASSWORD"],
            "HOST": postgres_values["POSTGRES_HOST"],
            "PORT": postgres_values["POSTGRES_PORT"],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / env("SQLITE_NAME", "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = env("TIME_ZONE", "Europe/Moscow")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
SERVE_MEDIA_FILES = env_bool("DJANGO_SERVE_MEDIA_FILES", "False")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "public_lead": env("RATE_LIMIT_PUBLIC_LEAD", "60/minute"),
        "public_event": env("RATE_LIMIT_PUBLIC_EVENT", "120/minute"),
        "public_analytics_event": env("RATE_LIMIT_PUBLIC_ANALYTICS_EVENT", "300/minute"),
        "public_telegram_webhook": env("RATE_LIMIT_PUBLIC_TELEGRAM_WEBHOOK", "120/minute"),
    },
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(env("JWT_ACCESS_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(env("JWT_REFRESH_DAYS", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

REDIS_URL = env("REDIS_URL", "")
IS_TEST_MODE = "test" in sys.argv
USE_REDIS_CACHE = bool(REDIS_URL) and not IS_TEST_MODE
if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "yadro",
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", not IS_PRODUCTION)
CORS_ALLOWED_ORIGINS = env_csv(
    "CORS_ALLOWED_ORIGINS",
    "" if IS_PRODUCTION else ",".join(DEFAULT_CORS_ORIGINS),
)
CORS_ALLOWED_ORIGIN_REGEXES = env_csv("CORS_ALLOWED_ORIGIN_REGEXES", "")
CORS_ALLOW_CREDENTIALS = True
if IS_PRODUCTION and CORS_ALLOW_ALL_ORIGINS:
    raise ImproperlyConfigured("CORS_ALLOW_ALL_ORIGINS must be false in production")

DEFAULT_CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CSRF_TRUSTED_ORIGINS = env_csv(
    "CSRF_TRUSTED_ORIGINS",
    "" if IS_PRODUCTION else ",".join(DEFAULT_CSRF_TRUSTED_ORIGINS),
)

DOMAIN = required_env("DOMAIN") if IS_PRODUCTION else env("DOMAIN", "localhost")
if IS_PRODUCTION and DOMAIN in {"localhost", "127.0.0.1", "0.0.0.0"}:
    raise ImproperlyConfigured("DOMAIN cannot use a local address in production")
SITE_BASE_URL = public_url(
    "SITE_BASE_URL",
    "http://localhost:8000",
    aliases=("BACKEND_URL", "SITE_URL"),
)
PUBLIC_BASE_URL = public_url(
    "PUBLIC_BASE_URL",
    SITE_BASE_URL,
    aliases=("PUBLIC_SITE_URL",),
)
FRONTEND_URL = public_url("FRONTEND_URL", SITE_BASE_URL)
API_URL = public_url("API_URL", f"{SITE_BASE_URL}/api")
ADMIN_URL = public_url("ADMIN_URL", f"{SITE_BASE_URL}/admin")
SEO_AUDIT_USER_AGENT = env(
    "SEO_AUDIT_USER_AGENT",
    f"TrackNode SEO Audit/1.0 (+{SITE_BASE_URL})",
)
if IS_PRODUCTION:
    invalid_origins = [
        origin
        for origin in (*CORS_ALLOWED_ORIGINS, *CSRF_TRUSTED_ORIGINS)
        if urlparse(origin).scheme not in {"http", "https"}
        or urlparse(origin).hostname in {"localhost", "127.0.0.1", "0.0.0.0", None}
        or (REQUIRE_HTTPS and urlparse(origin).scheme != "https")
    ]
    if invalid_origins:
        raise ImproperlyConfigured(
            "CORS and CSRF origins must use public HTTP(S) URLs matching DJANGO_REQUIRE_HTTPS"
        )
    has_local_cors_regex = any(
        local in regex
        for regex in CORS_ALLOWED_ORIGIN_REGEXES
        for local in ("localhost", "127.0.0.1")
    )
    if has_local_cors_regex:
        raise ImproperlyConfigured("CORS_ALLOWED_ORIGIN_REGEXES cannot contain local addresses in production")
    if urlparse(SITE_BASE_URL).scheme == "http" and (
        SECURE_SSL_REDIRECT or SESSION_COOKIE_SECURE or CSRF_COOKIE_SECURE
    ):
        raise ImproperlyConfigured(
            "HTTP production URLs require SSL redirect and secure cookies to be disabled"
        )
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = env("TELEGRAM_BOT_USERNAME", "").lstrip("@")
TELEGRAM_WEBHOOK_SECRET = env("TELEGRAM_WEBHOOK_SECRET", "")
TELEGRAM_USE_WEBHOOK = env_bool("TELEGRAM_USE_WEBHOOK", False)
TELEGRAM_BIND_TOKEN_MAX_AGE = int(env("TELEGRAM_BIND_TOKEN_MAX_AGE", "3600"))

YOOKASSA_SHOP_ID = env("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = env("YOOKASSA_SECRET_KEY", "")
YOOKASSA_RETURN_URL = env("YOOKASSA_RETURN_URL", f"{SITE_BASE_URL}/dashboard")
PAYMENT_RETURN_URL = env("PAYMENT_RETURN_URL", YOOKASSA_RETURN_URL)
PAYMENT_CHECKOUT_URL = env("PAYMENT_CHECKOUT_URL", "")
ENABLE_BILLING = env_bool("ENABLE_BILLING", False)

OPENAI_API_KEY = env("OPENAI_API_KEY", "").strip()
OPENAI_MODEL_SEO = env("OPENAI_MODEL_SEO", "gpt-5-mini").strip() or "gpt-5-mini"
OPENAI_MODEL_CONVERSION = env("OPENAI_MODEL_CONVERSION", "gpt-5-mini").strip() or "gpt-5-mini"
AI_RECOMMENDATIONS_ENABLED = env_bool("AI_RECOMMENDATIONS_ENABLED", False)
AI_RECOMMENDATIONS_TIMEOUT_SECONDS = float(env("AI_RECOMMENDATIONS_TIMEOUT_SECONDS", "20"))
AI_RECOMMENDATIONS_TTL_SECONDS = int(env("AI_RECOMMENDATIONS_TTL_SECONDS", "10800"))
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS = int(env("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS", "900"))
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_SEO = int(
    env("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_SEO", "700")
)
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_CONVERSION = int(
    env("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_CONVERSION", str(AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS))
)
AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_RETRY_CAP = int(
    env("AI_RECOMMENDATIONS_MAX_OUTPUT_TOKENS_RETRY_CAP", "1200")
)

AUTHENTICATION_BACKENDS = [
    "accounts.auth_backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]

REPORTS_STORAGE_DIR = BASE_DIR / "reports_storage"

CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL",
    REDIS_URL or ("" if IS_PRODUCTION else "redis://localhost:6379/1"),
)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "send_daily_pdf_at_20_msk": {
        "task": "reports.tasks.send_daily_pdf.send_daily_pdf_task",
        "schedule": timedelta(hours=24),
    },
    "notify_auto_renew_subscriptions_daily": {
        "task": "subscriptions.tasks.notify_auto_renew_subscriptions_task",
        "schedule": timedelta(hours=24),
    },
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
