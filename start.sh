#!/bin/sh
set -e

echo "🔧 Running Django migrations..."
python manage.py migrate

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "👤 Creating superusers if they don't exist..."
echo "
from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='test_admin').exists():
    User.objects.create_superuser('test_admin', 'test_admin@example.com', '@QAZ123')
    print('✅ Superuser test_admin created.')

if not User.objects.filter(username='test_sassan').exists():
    User.objects.create_superuser('test_sassan', 'test_sassan@example.com', '@123')
    print('✅ Superuser test_sassan created.')
" | python manage.py shell

echo "🚀 Starting Gunicorn server..."
gunicorn scm.wsgi:application --bind 0.0.0.0:8000 --workers=1
