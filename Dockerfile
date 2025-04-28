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
RUN pip install --no-cache-dir gunicorn whitenoise

# Copy project
COPY . .

# Run as non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Run migrations, collect static, create superusers, then start app
CMD ["sh", "-c", "\
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    echo \"from django.contrib.auth import get_user_model; User = get_user_model(); \
    | python manage.py shell && \
    gunicorn scm.wsgi:application --bind 0.0.0.0:8000 --workers=1"]
