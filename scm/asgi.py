"""
WSGI config for scm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Get environment from DJANGO_ENVIRONMENT or default to development
environment = os.environ.get("DJANGO_ENVIRONMENT", "development")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"scm.settings.{environment}")

application = get_wsgi_application()
