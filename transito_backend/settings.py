

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-4+3tbsm^#gh*4-%6)va$*kr7_2_%j*bzetczczw@p#ph3+3+@+')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',') if os.getenv('DJANGO_ALLOWED_HOSTS') else []

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS') else []
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

# Application definition

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_APPS = [
    'whitenoise.runserver_nostatic',
    'apps.common.apps.CommonConfig',
    'tailwind',
    "theme",
]

MY_APPS = [
    'apps.mandantes',
    'apps.proyectos',
    'apps.red_vial',
    'apps.tasks',
    'apps.usuarios',
]

INSTALLED_APPS = BASE_APPS + THIRD_APPS + MY_APPS

if DEBUG:
    # Add django_browser_reload only in DEBUG mode
    INSTALLED_APPS += ["django_browser_reload"]

TAILWIND_APP_NAME = "theme"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'apps.common.db_router.DatabaseSelectorMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

if DEBUG:
    # Add django_browser_reload middleware only in DEBUG mode
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]

ROOT_URLCONF = 'transito_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.common.context_processors.pending_tasks',
            ],
        },
    },
]

WSGI_APPLICATION = 'transito_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


####### DEFAULT DATABASE CONFIGURATION #######


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

####### LOCAL PG DATABASE CONFIGURATION #######

# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://postgres:1234@localhost:5432/eitapp',
#         conn_max_age=600
#     )
# }



####### DATABASE CONFIGURATION #######

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        conn_max_age=int(os.getenv('CONN_MAX_AGE', '0')),
    ),
}

# ── ORA: PostgreSQL en VPS (Coolify / Oracle Cloud) ──
# Toma las vars individuales del .env: host, user, password, port, dbname
_url_ora = os.getenv('DATABASE_URL_ORA')
if not _url_ora:
    _user = os.getenv("user")
    _password = os.getenv("password")
    _host = os.getenv("host")
    _port = os.getenv("port")
    _dbname = os.getenv("dbname")
    if all([_user, _password, _host, _port, _dbname]):
        _url_ora = f"postgresql://{_user}:{_password}@{_host}:{_port}/{_dbname}"
if _url_ora:
    DATABASES["ORA"] = dj_database_url.parse(
        _url_ora,
        conn_max_age=int(os.getenv('CONN_MAX_AGE', '0')),
    )

# ── supa: PostgreSQL en Supabase (referencia, solo si se definen las vars) ──
_supa_url = os.getenv('DATABASE_URL_SUPA')
if not _supa_url:
    _su = os.getenv("supa_user") or os.getenv("SUPA_USER")
    _sp = os.getenv("supa_password") or os.getenv("SUPA_PASSWORD")
    _sh = os.getenv("supa_host") or os.getenv("SUPA_HOST")
    _spt = os.getenv("supa_port") or os.getenv("SUPA_PORT")
    _sd = os.getenv("supa_dbname") or os.getenv("SUPA_DBNAME")
    if all([_su, _sp, _sh, _spt, _sd]):
        _supa_url = f"postgresql://{_su}:{_sp}@{_sh}:{_spt}/{_sd}"
if _supa_url:
    DATABASES["supa"] = dj_database_url.parse(_supa_url, conn_max_age=0)

# ── pg_local: PostgreSQL local (tu máquina) ──
DATABASES["pg_local"] = dj_database_url.config(
    env='DATABASE_URL_LOCAL',
    default='postgresql://postgres:1234@localhost:5432/eitapp',
    conn_max_age=600,
)

DATABASE_ROUTERS = ['apps.common.db_router.ActiveDatabaseRouter']

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# LANGUAGE_CODE = 'es-cl'
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
# TIME_ZONE = 'America/Santiago'
USE_TZ = True

USE_I18N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "apps/common/static"),  
]

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/signin'


# Enable the WhiteNoise storage backend in production, which compresses static files
# to reduce disk use and renames files with unique names for long-term caching
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
