# SmartMove Application

This is the SmartMove application - a unified Flask backend and React frontend for moving services.

## Architecture Overview

SmartMove is a merged application where:

- **Flask backend** serves REST API endpoints at `/api/*`
- **React frontend** is served as static files by Flask in production
- **Development mode** allows running backend and frontend separately with hot-reloading
- **Production mode** serves both from a single Flask server

## Quick Start

### Development Mode (Recommended for Development)

Run backend and frontend separately with hot-reloading:

**Terminal 1 - Backend:**

```bash
python run.py
```

**Terminal 2 - Frontend:**

```bash
cd smartmovefrontend/smartmove
npm run dev
```

The frontend will be available at `http://localhost:5173` and will proxy API requests to the backend at `http://localhost:5001`.

### Production Mode (Single Server)

Build and run the entire application from Flask:

```bash
# Build the frontend
bash scripts/build_frontend.sh

# Run the Flask server
python run.py
```

The application will be available at `http://localhost:5001` serving both API and frontend.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Local Installation](#local-installation)
  - [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)
  - [Running in Development Mode](#running-in-development-mode)
  - [Running in Production Mode](#running-in-production-mode)
- [Build Process](#build-process)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Celery Background Tasks](#celery-background-tasks)
- [Deployment](#deployment)
  - [Docker Deployment](#docker-deployment)
  - [Railway Deployment](#railway-deployment)
  - [Render Deployment](#render-deployment)
- [Troubleshooting](#troubleshooting)

## Features

- **Unified Deployment**: Single server serves both API and frontend in production
- **Development Flexibility**: Run backend and frontend separately with hot-reloading
- **API Routing**: All API endpoints prefixed with `/api/` for clear separation
- **SPA Support**: Client-side routing with React Router, direct URL access to any route
- **MPESA Integration**: STK Push for payments with callback mechanism
- **Real-time Updates**: WebSocket support for notifications and chat
- **Background Tasks**: Celery integration for async operations

## Setup

### Prerequisites

**Backend:**

- Python 3.9+
- pip (Python package installer)
- virtualenv or conda (recommended)
- PostgreSQL (recommended for production) or SQLite (for local development)
- Redis (for Celery message broker)

**Frontend:**

- Node.js 18+ and npm
- Modern web browser

### Local Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repo/smartmove.git
   cd smartmove
   ```

2. **Backend Setup:**

   ```bash
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**

   ```bash
   cd smartmovefrontend/smartmove
   npm install
   cd ../..
   ```

4. **Database Setup:**

   ```bash
   # Initialize database
   flask db upgrade

   # (Optional) Seed with sample data
   python scripts/seed_data.py
   ```

### Environment Variables

#### Backend Environment Variables

Create a `.env` file in the root directory:

```ini
# Flask Configuration
SECRET_KEY='your_super_secret_key_here'
FLASK_ENV='development'  # or 'production'
FLASK_APP='wsgi:app'

# Database
DATABASE_URL='sqlite:///app.db'  # For local development
# DATABASE_URL='postgresql://user:password@host:port/database'  # For production

# Celery (Background Tasks)
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'

# MPESA Payment Integration
MPESA_BASE_URL='https://sandbox.safaricom.co.ke'  # Or production URL
MPESA_CONSUMER_KEY='your_mpesa_consumer_key'
MPESA_CONSUMER_SECRET='your_mpesa_consumer_secret'
MPESA_SHORTCODE='your_mpesa_shortcode'
MPESA_PASSKEY='your_mpesa_passkey'
CALLBACK_URL='https://your_backend_url.com/api/payments/callback'

# Email Service (Optional)
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME='your_email@gmail.com'
MAIL_PASSWORD='your_email_password'

# Google Maps API (Optional)
GOOGLE_MAPS_API_KEY='your_google_maps_api_key'
```

#### Frontend Environment Variables

Create `smartmovefrontend/smartmove/.env`:

```ini
# Development - proxy to local backend
VITE_API_BASE_URL=http://localhost:5001/api

# Production - use relative path (served from same origin)
# VITE_API_BASE_URL=/api
```

**Note:** In production, the frontend uses `/api` by default, so you typically don't need to set `VITE_API_BASE_URL` for production builds.

## Development Workflow

### Running in Development Mode

Development mode runs backend and frontend as separate processes, enabling hot-reloading for both.

**Terminal 1 - Start Backend:**

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask development server
python run.py
```

Backend will run on `http://localhost:5001`

**Terminal 2 - Start Frontend:**

```bash
cd smartmovefrontend/smartmove
npm run dev
```

Frontend will run on `http://localhost:5173` with Vite dev server.

**Terminal 3 - Start Celery (Optional):**

```bash
# Activate virtual environment
source venv/bin/activate

# Run Celery worker
celery -A celery_app.celery_app worker --loglevel=info
```

**Development Features:**

- Hot module replacement (HMR) for frontend changes
- Flask auto-reload for backend changes
- API requests automatically proxied from frontend to backend
- CORS configured for cross-origin requests

### Running in Production Mode

Production mode serves both frontend and backend from a single Flask server.

**Step 1 - Build Frontend:**

```bash
bash scripts/build_frontend.sh
```

This creates a `build/` directory with compiled frontend assets.

**Step 2 - Run Flask Server:**

```bash
# Using Flask directly
python run.py

# Or using Gunicorn (recommended for production)
gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 4
```

Application will be available at `http://localhost:5001` (or port 8000 with Gunicorn).

**Production Features:**

- Single server serves both API and frontend
- Static files cached with appropriate headers
- No CORS needed (same-origin requests)
- SPA routing fully supported

## Build Process

### Frontend Build Script

The `scripts/build_frontend.sh` script handles the frontend build process:

```bash
bash scripts/build_frontend.sh
```

**What it does:**

1. Navigates to frontend directory
2. Installs npm dependencies if needed
3. Runs Vite build process
4. Outputs compiled files to `build/` directory

**Build Output:**

```
build/
├── index.html           # Main HTML file
├── assets/
│   ├── index-[hash].js  # Bundled JavaScript
│   ├── index-[hash].css # Bundled CSS
│   └── [images]         # Optimized images
└── ...
```

### Manual Build Steps

If you prefer to build manually:

```bash
cd smartmovefrontend/smartmove
npm install
npm run build
cd ../..
```

The build output will be in `build/` at the project root.

## Database Migrations

This project uses Flask-Migrate (Alembic) for database migrations.

**Create a new migration:**

```bash
flask db migrate -m "Description of changes"
```

**Apply migrations:**

```bash
flask db upgrade
```

**Rollback migrations:**

```bash
flask db downgrade
```

**View migration history:**

```bash
flask db history
```

## Testing

### Backend Tests

Run Python tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_models/test_user_model.py

# Run with verbose output
pytest -v
```

### Frontend Tests

Run JavaScript tests:

```bash
cd smartmovefrontend/smartmove
npm test
```

## Celery Background Tasks

Celery handles asynchronous tasks like sending emails and notifications.

**Start Celery worker:**

```bash
celery -A celery_app.celery_app worker --loglevel=info
```

**Start Celery beat (for scheduled tasks):**

```bash
celery -A celery_app.celery_app beat --loglevel=info
```

**Monitor tasks with Flower:**

```bash
celery -A celery_app.celery_app flower
```

Access Flower dashboard at `http://localhost:5555`

## Deployment

### Docker Deployment

The application includes a Dockerfile for containerized deployment.

**Build Docker image:**

```bash
docker build -t smartmove:latest .
```

**Run Docker container:**

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY='your_secret_key' \
  -e DATABASE_URL='your_database_url' \
  smartmove:latest
```

**Using Docker Compose:**

```bash
docker-compose up -d
```

**What the Dockerfile does:**

1. Installs Python and Node.js
2. Installs backend dependencies
3. Builds frontend (runs `npm install` and `npm run build`)
4. Copies build output to Flask static folder
5. Runs database migrations on startup
6. Starts Gunicorn server

### Railway Deployment

Railway provides easy deployment with automatic builds.

**Steps:**

1. **Create Railway Project:**
   - Go to [Railway](https://railway.app)
   - Create new project from GitHub repo

2. **Configure Environment Variables:**

   In Railway dashboard, add these variables:

   ```
   SECRET_KEY=your_secret_key
   FLASK_ENV=production
   DATABASE_URL=<auto-populated by Railway Postgres>
   MPESA_CONSUMER_KEY=your_key
   MPESA_CONSUMER_SECRET=your_secret
   MPESA_SHORTCODE=your_shortcode
   MPESA_PASSKEY=your_passkey
   CALLBACK_URL=https://your-app.railway.app/api/payments/callback
   ```

3. **Add PostgreSQL Database:**
   - Add Railway Postgres plugin
   - `DATABASE_URL` will be auto-populated

4. **Add Redis (for Celery):**
   - Add Railway Redis plugin
   - Set `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`

5. **Deploy:**
   - Railway automatically detects `Procfile` and deploys
   - The `start.sh` script builds frontend and starts server
   - Migrations run automatically on startup

6. **Verify Deployment:**
   - Check logs in Railway dashboard
   - Visit your app URL
   - Test API endpoints at `/api/health`

### Render Deployment

Render provides similar deployment capabilities.

**Steps:**

1. **Create Web Service:**
   - Go to [Render](https://render.com)
   - Create new Web Service from GitHub repo

2. **Configure Build & Start:**
   - Build Command: `pip install -r requirements.txt && bash scripts/build_frontend.sh`
   - Start Command: `bash start.sh`

3. **Environment Variables:**

   Add in Render dashboard:

   ```
   SECRET_KEY=your_secret_key
   FLASK_ENV=production
   DATABASE_URL=<from Render Postgres>
   MPESA_CONSUMER_KEY=your_key
   MPESA_CONSUMER_SECRET=your_secret
   MPESA_SHORTCODE=your_shortcode
   MPESA_PASSKEY=your_passkey
   CALLBACK_URL=https://your-app.onrender.com/api/payments/callback
   ```

4. **Add PostgreSQL:**
   - Create Render PostgreSQL database
   - Link to web service

5. **Add Redis:**
   - Create Render Redis instance
   - Set Celery environment variables

6. **Deploy:**
   - Render builds and deploys automatically
   - Monitor logs for any issues

## Troubleshooting

### Common Issues and Solutions

#### 1. Frontend Not Loading in Production

**Symptoms:**

- Blank page when accessing root URL
- 404 errors for static files

**Solutions:**

```bash
# Rebuild frontend
bash scripts/build_frontend.sh

# Verify build directory exists
ls -la build/

# Check Flask logs for static folder warnings
python run.py
```

**Check:**

- Ensure `build/` directory exists and contains `index.html`
- Verify Flask `static_folder` configuration in `app/__init__.py`
- Check browser console for errors

#### 2. API Requests Failing (404 Not Found)

**Symptoms:**

- API calls return 404
- CORS errors in browser console

**Solutions:**

**Development Mode:**

```bash
# Verify backend is running on port 5001
curl http://localhost:5001/api/health

# Check Vite proxy configuration
cat smartmovefrontend/smartmove/vite.config.mjs
```

**Production Mode:**

```bash
# Verify API prefix is correct
curl http://localhost:5001/api/health

# Check that all API routes have /api/ prefix
```

**Check:**

- All API endpoints should be prefixed with `/api/`
- Frontend should use `API_BASE_URL` from config
- CORS should be enabled in development mode

#### 3. CORS Errors in Development

**Symptoms:**

- "Access-Control-Allow-Origin" errors in browser console
- API requests blocked by browser

**Solutions:**

```bash
# Verify FLASK_ENV is set to development
echo $FLASK_ENV

# Check CORS configuration in app/__init__.py
# Should allow localhost:5173 origin
```

**Fix:**

```python
# In app/__init__.py
if os.environ.get('FLASK_ENV') == 'development':
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
            "supports_credentials": True
        }
    })
```

#### 4. Build Script Fails

**Symptoms:**

- `scripts/build_frontend.sh` exits with error
- "npm: command not found" or similar

**Solutions:**

```bash
# Install Node.js and npm
# macOS:
brew install node

# Ubuntu/Debian:
sudo apt-get install nodejs npm

# Verify installation
node --version
npm --version

# Clear npm cache and retry
cd smartmovefrontend/smartmove
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 5. Database Migration Errors

**Symptoms:**

- "No such table" errors
- Migration conflicts

**Solutions:**

```bash
# Check current migration status
flask db current

# Apply all pending migrations
flask db upgrade

# If migrations are out of sync, reset (CAUTION: loses data)
rm -rf migrations/versions/*.py
flask db migrate -m "Initial migration"
flask db upgrade
```

#### 6. Environment Variables Not Loading

**Symptoms:**

- "KeyError" for environment variables
- Default values being used

**Solutions:**

```bash
# Verify .env file exists
ls -la .env

# Check .env is not in .gitignore (it should be)
cat .gitignore | grep .env

# Load environment variables manually
export $(cat .env | xargs)

# Verify variables are set
echo $SECRET_KEY
echo $DATABASE_URL
```

#### 7. Port Already in Use

**Symptoms:**

- "Address already in use" error
- Cannot start Flask or Vite

**Solutions:**

```bash
# Find process using port 5001 (Flask)
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=5002 python run.py
```

#### 8. Static Files Not Cached

**Symptoms:**

- Slow page loads
- Assets re-downloaded on every request

**Solutions:**

- Verify cache headers are set in `app/__init__.py`
- Check browser DevTools Network tab for cache-control headers
- Ensure hashed filenames are used for assets (Vite does this automatically)

#### 9. SPA Routes Return 404 on Refresh

**Symptoms:**

- Direct navigation to `/dashboard` works
- Refreshing on `/dashboard` returns 404

**Solutions:**

- Verify catch-all route is registered in `app/__init__.py`
- Check route priority (API routes should be registered before catch-all)
- Ensure `serve_spa` function serves `index.html` for non-API routes

```python
# In app/__init__.py
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_spa(path):
    # Should serve index.html for non-API, non-static paths
    pass
```

#### 10. Celery Tasks Not Running

**Symptoms:**

- Background tasks not executing
- No Celery worker logs

**Solutions:**

```bash
# Verify Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
redis-server

# Start Celery worker with verbose logging
celery -A celery_app.celery_app worker --loglevel=debug

# Check Celery configuration
python -c "from celery_app import celery_app; print(celery_app.conf)"
```

### Getting Help

If you encounter issues not covered here:

1. **Check Logs:**
   - Flask logs: Check terminal output or `app.log`
   - Browser console: Check for JavaScript errors
   - Network tab: Check API request/response details

2. **Verify Configuration:**
   - Environment variables are set correctly
   - Database connection is working
   - Redis is running (for Celery)

3. **Test Components Separately:**
   - Test backend API with curl or Postman
   - Test frontend in development mode
   - Test database connection

4. **Common Commands:**

   ```bash
   # Check Python version
   python --version

   # Check Node version
   node --version

   # Check installed packages
   pip list
   npm list

   # Test database connection
   flask shell
   >>> from app import db
   >>> db.engine.execute('SELECT 1').scalar()
   ```

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Docker Documentation](https://docs.docker.com/)

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
