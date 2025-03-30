from dotenv import load_dotenv
from .base import *  # noqa
from .base import BASE_DIR
from os import getenv, path

# Load environment variables from .env.production file
prod_env_file = path.join(BASE_DIR, ".envs", ".env.production")
if path.isfile(prod_env_file):
    load_dotenv(prod_env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = getenv("ALLOWED_HOSTS").split(",")

# Database - PostgreSQL for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": getenv("DB_NAME"),
        "USER": getenv("DB_USER"),
        "PASSWORD": getenv("DB_PASSWORD"),
        "HOST": getenv("DB_HOST"),
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

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Disable Swagger in production by default
# Industry standard is to either disable or heavily restrict in production
SWAGGER_SETTINGS = {
    "ENABLED": getenv("ENABLE_SWAGGER", "False") == "True",
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": False,
}

# Restrict Swagger access in production to staff users
SWAGGER_PERMISSION_CLASSES = ["rest_framework.permissions.IsAdminUser"]
