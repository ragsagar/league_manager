# Use Python 3.11-slim as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=league_manager.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/media /app/staticfiles

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Create a non-root user
RUN useradd --create-home --shell /bin/bash league_manager
RUN usermod -a -G league_manager league_manager

# Change ownership of the app directory
RUN chown -R league_manager:league_manager /app

# Switch to non-root user
USER league_manager

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "league_manager.wsgi:application"]

