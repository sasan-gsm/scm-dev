# Use slim Python base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
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

# Copy project files
COPY . .

# Copy the startup script
COPY start.sh /app/start.sh

# Make startup script executable
RUN chmod +x /app/start.sh

# Create a non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Use the script to run all setup and start the server
CMD ["sh", "/app/start.sh"]
