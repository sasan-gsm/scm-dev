from pathlib import Path
from dotenv import load_dotenv
from os import getenv, path
from loguru import logger
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

local_env_file = path.join(BASE_DIR, ".envs", ".env.development")

if path.isfile(local_env_file):
    load_dotenv(local_env_file)

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_countries",
    "phonenumber_field",
    "drf_yasg",
    "corsheaders",
    "django_filters",
    "djcelery_email",
    "rest_framework_simplejwt",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",  # Optional: for social authentication
    "dj_rest_auth",
    "rest_framework.authtoken",
    "dj_rest_auth.registration",
    # "haystack",
    # "drf_haystack",
]

LOCAL_APPS = [
    "core.common",
    "core.accounts",
    "core.projects",
    "core.materials",
    "core.request",
    "core.procurement",
    "core.inventory",
    "core.quality",
    "core.accounting",
    "core.notifications",
    "core.attachments",
    "core.dashboard",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = (
    "core.accounts.backends.EmailPhoneUsernameAuthenticationBackend",  # custom authentication
    "allauth.account.auth_backends.AuthenticationBackend",  # Allows allauth authentication
    "core.accounts.backends.CustomPermissionBackend",
    "django.contrib.auth.backends.ModelBackend",
)

ROOT_URLCONF = "scm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "scm.wsgi.application"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

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
# Redis Cache Configuration
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "CONNECTION_POOL_KWARGS": {"max_connections": 100},
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#             "IGNORE_EXCEPTIONS": True,
#         },
#         "KEY_PREFIX": "SCM",
#     }
# }

# Cache time to live is 15 minutes (in seconds)
# CACHE_TTL = 60 * 15

# # Session cache configuration
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"

# Celery Configuration
CELERY_BROKER_URL = getenv("CELERY_BROKER")
CELERY_RESULT_BACKEND = getenv("CELERY_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

# Django REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # Fully stateless
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",  # Require authentication for all endpoints
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",  # For field filtering
        "rest_framework.filters.SearchFilter",  # For search functionality
        "rest_framework.filters.OrderingFilter",  # For ordering results
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",  # Enable pagination
    "PAGE_SIZE": 50,
    "PAGE_SIZE_QUERY_PARAM": "page_size",
    "MAX_PAGE_SIZE": 200,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # Throttle anonymous users
        "rest_framework.throttling.UserRateThrottle",  # Throttle authenticated users
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",  # Anonymous users: 100 requests per day
        "user": "5000/day",  # Authenticated users: 1000 requests per day
    },
}

# Swagger settings
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "PERSIST_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    "DEFAULT_MODEL_RENDERING": "model",
    "DEFAULT_INFO": "scm.urls.schema_view",
    "DOC_EXPANSION": "none",
}

# Redoc settings
REDOC_SETTINGS = {
    "LAZY_RENDERING": True,
    "HIDE_HOSTNAME": False,
    "EXPAND_RESPONSES": "all",
    "PATH_IN_MIDDLE": False,
}
# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=60
    ),  # Access token lifetime (e.g., 30 minutes)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # Refresh token lifetime (e.g., 1 day)
    "ROTATE_REFRESH_TOKENS": True,  # Automatically rotate refresh tokens
    "BLACKLIST_AFTER_ROTATION": False,  # No blacklisting
    "UPDATE_LAST_LOGIN": True,  # Update the user's last login time on token refresh
    "ALGORITHM": "HS256",  # Encryption algorithm
    "SIGNING_KEY": getenv("SECRET_KEY"),  # Use Django's SECRET_KEY for signing
    "VERIFYING_KEY": None,  # No verifying key for HS256
    "AUDIENCE": None,  # No audience
    "ISSUER": None,  # No issuer
    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),  # Authorization header type (e.g., Bearer <token>)
    "USER_ID_FIELD": "id",  # Field to use as the user ID
    "USER_ID_CLAIM": "user_id",  # Claim to use as the user ID in the token
    "AUTH_TOKEN_CLASSES": (
        "rest_framework_simplejwt.tokens.AccessToken",
    ),  # Token classes
}
# dj-rest-auth
REST_AUTH = {
    "USE_JWT": True,  # Use JWT tokens
    "JWT_AUTH_COOKIE": None,  # No cookie-based JWT
    "JWT_AUTH_REFRESH_COOKIE": None,
    "REGISTER_SERIALIZER": "core.accounts.serializers.CustomRegisterSerializer",  # Updated path
    "LOGIN_SERIALIZER": "core.accounts.serializers.CustomLoginSerializer",  # Updated path
    "PASSWORD_RESET_SERIALIZER": "core.accounts.serializers.CustomPasswordResetSerializer",  # Updated path
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "core.accounts.serializers.CustomPasswordResetConfirmSerializer",  # Updated path
    "PASSWORD_CHANGE_SERIALIZER": "core.accounts.serializers.CustomPasswordChangeSerializer",  # Updated path
    "USER_DETAILS_SERIALIZER": "core.accounts.serializers.UserDetailsSerializer",  # Updated path
}

ACCOUNT_AUTHENTICATION_METHOD = "username"  # Allow both username and email
ACCOUNT_EMAIL_REQUIRED = False  # Require email for signup
ACCOUNT_UNIQUE_EMAIL = True  # Ensure email is unique
ACCOUNT_USERNAME_REQUIRED = True  # Make username mandatory
ACCOUNT_EMAIL_VERIFICATION = "optional"  # Require email verification
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7  # Expiration for confirmation emails

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

SITE_ID = 1

ADMIN_URL = "secretgateway/"

STATIC_URL = "/static/"

STATIC_ROOT = path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/mediafiles/"

MEDIA_ROOT = str(BASE_DIR / "mediafiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_URLS_REGEX = r"^/api/.*$"

LOGGING_CONFIG = None

LOGURU_LOGGING = {
    "handlers": [
        {
            "sink": BASE_DIR / "logs/debug.log",
            "level": "DEBUG",
            "filter": lambda record: record["level"].no <= logger.level("WARNING").no,
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - "
            "{message}",
            "rotation": "10MB",
            "retention": "30 days",
            "compression": "zip",
        },
        {
            "sink": BASE_DIR / "logs/error.log",
            "level": "ERROR",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - "
            "{message}",
            "rotation": "10MB",
            "retention": "30 days",
            "compression": "zip",
            "backtrace": True,
            "diagnose": True,
        },
    ],
}
logger.configure(**LOGURU_LOGGING)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"loguru": {"class": "interceptor.InterceptHandler"}},
    "root": {"handlers": ["loguru"], "level": "DEBUG"},
}
