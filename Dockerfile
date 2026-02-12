FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required by some Python packages (e.g. psycopg2) and Node.js
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   libpq-dev \
	   curl \
	&& curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
	&& apt-get install -y nodejs \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
COPY requirements-dev.txt ./
# Copy wait-for-db script and make it executable
COPY wait-for-db.py /usr/local/bin/wait-for-db
RUN chmod +x /usr/local/bin/wait-for-db
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy frontend source


# Build frontend

# Return to app root
WORKDIR /app

# Copy application source (for builder if needed, but primarily for understanding context)
COPY . /app

# --- Production Stage ---
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install only essential runtime system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only production Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/celery /usr/local/bin/celery
COPY --from=builder /usr/local/bin/flask /usr/local/bin/flask
# Copy the wait-for-db script from the builder stage
COPY --from=builder /usr/local/bin/wait-for-db /usr/local/bin/wait-for-db
COPY requirements.txt .

# Copy application source
COPY . /app

# Copy frontend build output from builder stage
COPY --from=builder /app/build /app/build

# Create a non-root user and adjust ownership
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Set Flask app for potential CLI usage
ENV FLASK_APP=wsgi:app

# Use gunicorn config file for consistent settings
CMD ["gunicorn", "wsgi:app", "--config", "gunicorn.conf.py"]
