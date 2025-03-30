from dotenv import load_dotenv
from .base import *  # noqa
from .base import BASE_DIR
from os import getenv, path
from datetime import timedelta

local_env_file = path.join(BASE_DIR, ".envs", ".env.development")

if path.isfile(local_env_file):
    load_dotenv(local_env_file)

SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG")

SITE_NAME = getenv("SITE_NAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Database configuration for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INTERNAL_IPS = ["127.0.0.1"]

ADMIN_URL = getenv("ADMIN_URL")

EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")
DOMAIN = getenv("DOMAIN")
ADMIN_EMAIL = getenv("ADMIN_EMAIL")

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "PERSIST_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
}

# Override the permission classes for Swagger in development
SWAGGER_PERMISSION_CLASSES = ["rest_framework.permissions.AllowAny"]

MAX_UPLOAD_SIZE = 1 * 1024 * 1024

CSRF_TRUSTED_ORIGINS = ["http://localhost:8080"]

LOCKOUT_DURATION = timedelta(minutes=1)

LOGIN_ATTEMPTS = 3

OTP_EXPIRATION = timedelta(minutes=1)
