from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from botocore.config import Config as BotoConfig

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "django-insecure-4+3tbsm^#gh*4-%6)va$*kr7_2_%j*bzetczczw@p#ph3+3+@+"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = (
    [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
    if os.getenv("DJANGO_ALLOWED_HOSTS")
    else []
)

CSRF_TRUSTED_ORIGINS = (
    [h.strip() for h in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if h.strip()]
    if os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS")
    else []
)

# Application definition

BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_APPS = [
    "whitenoise.runserver_nostatic",
    "apps.common.apps.CommonConfig",
    "tailwind",
    "theme",
]

MY_APPS = [
    "apps.mandantes",
    "apps.proyectos",
    "apps.red_vial",
    "apps.tasks",
    "apps.usuarios",
]

INSTALLED_APPS = BASE_APPS + THIRD_APPS + MY_APPS

if DEBUG:
    # Add django_browser_reload only in DEBUG mode
    INSTALLED_APPS += ["django_browser_reload"]

TAILWIND_APP_NAME = "theme"
TAILWIND_STANDALONE_START_COMMAND_ARGS = (
    "-i static_src/src/styles.css -o static/css/dist/styles.css --watch=always"
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.common.db_router.DatabaseSelectorMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

if DEBUG:
    # Add django_browser_reload middleware only in DEBUG mode
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = "transito_backend.urls"

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
                "apps.common.context_processors.dev_banner",
                "apps.common.context_processors.pending_tasks",
            ],
        },
    },
]

WSGI_APPLICATION = "transito_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


####### DATABASE CONFIGURATION #######

# ── ORA: PostgreSQL en VPS (Coolify / Oracle Cloud) ──
_ora_url = os.getenv("DATABASE_URL_ORA")
if not _ora_url:
    _user = os.getenv("user")
    _password = os.getenv("password")
    _host = os.getenv("host")
    _port = os.getenv("port")
    _dbname = os.getenv("dbname")
    if all([_user, _password, _host, _port, _dbname]):
        _ora_url = f"postgresql://{_user}:{_password}@{_host}:{_port}/{_dbname}"

# default: DATABASE_URL > ORA > local PG fallback
# - Local: DATABASE_URL apunta a PG local, ORA disponible para switcheo
# - VPS (Coolify): DATABASE_URL no está seteada, cae a ORA automáticamente
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL") or _ora_url or "postgresql://postgres:1234@localhost:5432/eitapp",
        conn_max_age=int(os.getenv("CONN_MAX_AGE", "0")),
    ),
}

if _ora_url:
    DATABASES["ORA"] = dj_database_url.parse(
        _ora_url,
        conn_max_age=int(os.getenv("CONN_MAX_AGE", "0")),
    )

# ── pg_local: PostgreSQL local (para desarrollo, para switchear desde ORA) ──
DATABASES["pg_local"] = dj_database_url.config(
    env="DATABASE_URL_LOCAL",
    default="postgresql://postgres:1234@localhost:5432/eitapp",
    conn_max_age=600,
)

DATABASE_ROUTERS = ["apps.common.db_router.ActiveDatabaseRouter"]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# LANGUAGE_CODE = 'es-cl'
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"
# TIME_ZONE = 'America/Santiago'
USE_TZ = True

USE_I18N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "apps/common/static"),
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# ── Almacenamiento: OCI Object Storage (S3-compatible) o local ──
OCI_S3_ACCESS_KEY = os.getenv("OCI_S3_ACCESS_KEY", "")
OCI_S3_SECRET_KEY = os.getenv("OCI_S3_SECRET_KEY", "")
OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME", "")
OCI_S3_ENDPOINT = os.getenv("OCI_S3_ENDPOINT", "")
OCI_REGION = os.getenv("OCI_REGION", "us-phoenix-1")

_use_s3 = all([OCI_S3_ACCESS_KEY, OCI_S3_SECRET_KEY, OCI_BUCKET_NAME, OCI_S3_ENDPOINT])

if _use_s3:
    THIRD_APPS += ["storages"]
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": OCI_S3_ACCESS_KEY,
                "secret_key": OCI_S3_SECRET_KEY,
                "bucket_name": OCI_BUCKET_NAME,
                "endpoint_url": OCI_S3_ENDPOINT,
                "region_name": OCI_REGION,
                "default_acl": "public-read",
                "querystring_auth": False,
                "location": "media",
                "addressing_style": "path",
                "client_config": BotoConfig(
                    s3={"addressing_style": "path"},
                    signature_version="s3v4",
                    request_checksum_calculation="when_required",
                ),
            },
        },
    }
    STORAGES["staticfiles"] = (
        {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        }
        if not DEBUG
        else {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        }
    )
    MEDIA_URL = f"{OCI_S3_ENDPOINT}/{OCI_BUCKET_NAME}/media/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "/signin"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
