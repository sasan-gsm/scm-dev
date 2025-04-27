FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt requirements/base.txt
COPY requirements/development.txt requirements/development.txt
RUN pip install --no-cache-dir -r requirements/development.txt
RUN pip install --no-cache-dir gunicorn

# Copy project
COPY . .

# Run as non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run migrations, create superusers, and then start the app
CMD ["sh", "-c", "\
    python manage.py migrate && \
    echo \"from django.contrib.auth import get_user_model; User = get_user_model(); \
    User.objects.filter(username='test_admin').exists() or User.objects.create_superuser('test_admin', 'test_admin@example.com', '@QAZ123'); \
    User.objects.filter(username='test_sassan').exists() or User.objects.create_superuser('test_sassan', 'test_sassan@example.com', '@123')\" \
    | python manage.py shell && \
    gunicorn scm.wsgi:application --bind 0.0.0.0:8000"]
