from dotenv import load_dotenv
from .base import *  # noqa
from .base import BASE_DIR
from os import getenv, path

# Load environment variables from .env.staging file
staging_env_file = path.join(BASE_DIR, ".envs", ".env.staging")
if path.isfile(staging_env_file):
    load_dotenv(staging_env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS", "staging.example.com").split(",")

# Database - PostgreSQL for staging
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("DB_NAME"),
        "USER": getenv("DB_USER"),
        "PASSWORD": getenv("DB_PASSWORD"),
        "HOST": getenv("DB_HOST", "localhost"),
        "PORT": getenv("DB_PORT", "5432"),
    }
}

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
EMAIL_HOST_USER = getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = getenv("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")

# Security settings for staging
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Swagger settings - in staging, require authentication
# This follows industry standard for staging environments
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

# Restrict Swagger access in staging
SWAGGER_PERMISSION_CLASSES = ["rest_framework.permissions.IsAuthenticated"]
