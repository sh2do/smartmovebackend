# SmartMove Backend

This is the backend service for the SmartMove application, built with Flask.

## Quick Start: Running the Backend

To run the Flask application for local development:

```bash
python run.py
```
To run this in the background and continue using your terminal:
```bash
python run.py &
```

## Table of Contents

-   [Features](#features)
-   [Setup](#setup)
    -   [Prerequisites](#prerequisites)
    -   [Local Installation](#local-installation)
    -   [Environment Variables](#environment-variables)
-   [Running the Application](#running-the-application)
-   [Database Migrations](#database-migrations)
-   [Testing](#testing)
-   [Celery Background Tasks](#celery-background-tasks)
-   [Deployment](#deployment)

## Features

-   MPESA Integration: Supports STK Push for initiating payments and a callback mechanism to handle transaction results.

## Setup

### Prerequisites

-   Python 3.9+
-   pip (Python package installer)
-   (Optional) virtualenv or conda for virtual environments
-   PostgreSQL (recommended for production) or SQLite (for local development)
-   Redis (for Celery message broker)

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/smartmove-backend.git
    cd smartmove-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

Create a `.env` file in the root directory of the project, based on `.env.example`.

```ini
# .env file
SECRET_KEY='your_super_secret_key_here'
DATABASE_URL='sqlite:///app.db' # For local development with SQLite
# DATABASE_URL='postgresql://user:password@host:port/database' # For PostgreSQL
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'
# Add other environment variables as needed (e.g., API keys, email service credentials)
MPESA_BASE_URL='https://sandbox.safaricom.co.ke' # Or production URL
MPESA_CONSUMER_KEY='your_mpesa_consumer_key'
MPESA_CONSUMER_SECRET='your_mpesa_consumer_secret'
MPESA_SHORTCODE='your_mpesa_shortcode' # Paybill or Till Number
MPESA_PASSKEY='your_mpesa_passkey' # For STK Push
CALLBACK_URL='https://your_backend_url.com/payments/callback' # Your deployed backend callback URL
```

## Running the Application

For local development, you can run the Flask application directly:

```bash
python run.py
```

For production-like environments, use Gunicorn:

```bash
gunicorn --bind 0.0.0.0:${PORT:-8000} run:app
```
(Note: The gunicorn command here should be updated to reflect the `Dockerfile`'s CMD for consistency. The `wsgi:app` should likely be `run:app` based on the `Dockerfile` too.)

## Database Migrations

This project uses Flask-Migrate (Alembic) for database migrations.

To initialize a new migration:
```bash
flask db migrate -m "Initial migration"
```

To apply migrations:
```bash
flask db upgrade
```

To downgrade migrations:
```bash
flask db downgrade
```

## Testing

This project uses `pytest` for testing.

To run all tests:
```bash
pytest
```

## Celery Background Tasks

To run Celery workers for background tasks:

```bash
celery -A celery_app.celery_app worker --loglevel=info
```

## Deployment

Deployment is handled via Docker, with a `Dockerfile` configured for platforms like Railway. The `Dockerfile` handles database migrations automatically on startup.

---
**Note:** This `README.md` is a starting point and should be updated as the project evolves and specific features are implemented.
SmartMove Backend

Flask backend for SmartMove.

Deploying to Railway
--------------------

These steps will get the app deployed on Railway (https://railway.app). The repo includes a `Procfile` and `runtime.txt` so Railway's Python buildpack can detect and start the app.

1. Create a Railway project and connect your GitHub repo
	- Go to Railway and create a new project.
	- Connect your GitHub repository (this repo).

2. Build & Start command
	- This repo includes a `Procfile` with the web process:
	  - `web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 3 --log-file -`
	- Railway will detect Python from `runtime.txt` and `requirements.txt` and run the start command from the `Procfile`.

3. Required environment variables
	- Open your Railway project > Settings > Variables and set at minimum:
	  - `SECRET_KEY` — a secure random string for Flask.
	  - `DATABASE_URL` — a Postgres connection string if you provision a database (Railway Postgres plugin provides this automatically).
	- Optional/other env vars your instance needs (e.g., `FLASK_ENV`, external API keys).

4. Provision a database (optional but recommended)
	- In Railway, add the Postgres plugin to your project.
	- Railway will populate `DATABASE_URL` automatically; confirm it is present in Environment Variables.

5. Run database migrations / initialization
		- This repo has a `migrations/` folder. Use the included programmatic migration helper to apply migrations that use the Flask app's DB URL:
			- Locally: `python scripts/run_migrations.py`
			- On Railway (recommended via the project console): `railway run python scripts/run_migrations.py`
		- The script uses Alembic's programmatic API and reads `SQLALCHEMY_DATABASE_URI` from the Flask app config. If you prefer the raw Alembic CLI, you can also run:
			- `railway run alembic upgrade head`
		- If you have other initialization scripts, you can run them similarly:
			- `railway run python scripts/init_db.py` or `railway run python scripts/seed_data.py`.
		- You can run those commands from the Railway CLI or the project console in the web UI.

6. Check logs and verify
	- Use the Railway UI to view logs and confirm the `gunicorn` process started and is listening on the `$PORT` Railway provides.

Local testing
-------------

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Set environment variables locally (example):

```bash
export SECRET_KEY="my-local-secret"
export DATABASE_URL="sqlite:///app.db"
```

3. Run locally:

```bash
gunicorn run:app --bind 0.0.0.0:8000
```

Notes and troubleshooting
-------------------------
- Railway exposes the port in `$PORT`. The `Procfile` uses this variable so the service will bind correctly.
- If you prefer Docker, there's an existing `Dockerfile` and `docker-compose.yml` in the repo; you can instruct Railway to deploy from Docker instead of buildpack-based deploy.
- If migrations or initialization scripts are empty or not configured, confirm which management commands this repo expects and add them to `scripts/` or update the README accordingly.

If you'd like, I can also add a small Railway-specific helper (like a `railway.json` or documented `railway` CLI commands) or wire up a sample `alembic` command here—tell me which you'd prefer.
