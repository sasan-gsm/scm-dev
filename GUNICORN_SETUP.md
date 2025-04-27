# Gunicorn Setup for SCM Project

## Overview

This document provides instructions for replacing the default Django development server with Gunicorn for production deployments. Gunicorn (Green Unicorn) is a Python WSGI HTTP Server for UNIX that's broadly compatible with various web frameworks, simply implemented, light on server resources, and fairly fast.

## Files Added

1. **gunicorn.conf.py**: Configuration file for Gunicorn with optimized settings
2. **Dockerfile.prod**: Production-ready Dockerfile that uses Gunicorn
3. **docker-compose.prod.yml**: Production Docker Compose configuration
4. **scripts/gunicorn_start.sh**: Convenience script for starting Gunicorn
5. **Health check endpoint**: Added to core/common/views.py for monitoring

## How to Use

### Local Development

For local development, continue using the standard Django development server:

```bash
python manage.py runserver
```

Or with Docker:

```bash
docker-compose up
```

### Production Deployment

For production environments, use the production Docker setup:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

This will start the application using Gunicorn with the optimized settings defined in `gunicorn.conf.py`.

### Manual Gunicorn Start

If you need to start Gunicorn manually (without Docker):

```bash
gunicorn --config gunicorn.conf.py scm.wsgi:application
```

Or use the provided script:

```bash
bash scripts/gunicorn_start.sh
```

## Configuration

### Gunicorn Settings

The main Gunicorn configuration is in `gunicorn.conf.py`. Key settings include:

- **Workers**: Set to (2 × CPU cores + 1) for optimal performance
- **Timeout**: 120 seconds
- **Max Requests**: 1000 requests per worker before restart
- **Logging**: Configured to write to /var/log/gunicorn/

Adjust these settings based on your specific server resources and requirements.

### Environment Variables

The production Docker setup uses environment variables for configuration. These should be set in your deployment environment or provided in a `.env` file (not committed to version control).

## Health Checks

A health check endpoint is available at `/health/` which returns a simple JSON response with status "ok". This is used by Docker's healthcheck to monitor the application.

## Troubleshooting

### Common Issues

1. **Permission errors**: Ensure log directories exist and have proper permissions
2. **Connection refused**: Check that Gunicorn is binding to the correct address/port
3. **Worker timeout**: Increase the timeout setting if your application has long-running requests

### Logs

Check Gunicorn logs for issues:

```bash
cat /var/log/gunicorn/error.log
```

Or with Docker:

```bash
docker-compose -f docker-compose.prod.yml logs backend
```