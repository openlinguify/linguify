# Development Environment Setup Guide

This guide will help you set up the full development environment for **Linguify**, a language learning application with a Django backend and a Next.js frontend.

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 15+
- Git

## Backend Installation

### 1. Clone the repository

```bash
git clone https://github.com/linguify/linguify.git
cd linguify
```

### 2. Set up the Python environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the environment (Windows)
venv\Scripts\activate

# Activate the environment (macOS/Linux)
source venv/bin/activate

# Install dependencies using Poetry
cd backend
pip install poetry
poetry install
```

### 3. Set up the PostgreSQL database

```bash
# Create a database
createdb linguify

# Or using psql
psql -U postgres -c "CREATE DATABASE linguify;"
```

### 4. Configure the `.env` file

Create a `.env` file in the `backend/` folder with the following content:

```
# Django
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database configuration (PostgreSQL local)
# Development database
DEV_DB_NAME=db_linguify_dev
DEV_DB_USER=postgres
DEV_DB_PASSWORD=motdepasse
DEV_DB_HOST=localhost
DEV_DB_PORT=5432

# Production database
PROD_DB_NAME=db_linguify_prod
PROD_DB_USER=postgres
PROD_DB_PASSWORD=azerty
PROD_DB_HOST=localhost
PROD_DB_PORT=5432

# Test database
TEST_DB_NAME=db_linguify_test
TEST_DB_USER=postgres
TEST_DB_PASSWORD=azerty
TEST_DB_HOST=localhost
TEST_DB_PORT=5432

# Auth0
AUTH0_DOMAIN=your-tenant.region.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_AUDIENCE=https://linguify-api
AUTH0_ALGORITHM=RS256

# Application configuration
BACKEND_URL=http://localhost:8081
FRONTEND_URL=http://localhost:3000

# Email (optional for development)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=noreply@linguify.com
```

### 5. Apply migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start the backend development server

```bash
python manage.py runserver
```

## Frontend Installation

### 1. Go to the frontend directory

```bash
cd ../frontend
npm run dev:all
```

### 2. Install Node.js dependencies

```bash
npm install
# or with Yarn
yarn install
```

### 3. Set up the `.env.local` file

Create a `.env.local` file in the `frontend/` folder based on `.env.local.example`:

```
# Application configuration
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8081

# Auth0 configuration
NEXT_PUBLIC_AUTH0_DOMAIN=your-tenant.region.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your_client_id
NEXT_PUBLIC_AUTH0_REDIRECT_URI=http://localhost:3000/callback
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8081
NEXT_PUBLIC_AUTH0_AUDIENCE=https://linguify-api
```

### 4. Start the frontend development server

```bash
npm run dev:all 
It will run the frontend and the backend together
# or with Yarn
yarn dev
```

The frontend will be accessible at `http://localhost:3000`.

## Auth0 Configuration

1. Create an account at [Auth0](https://auth0.com/)
2. Create a new application (Regular Web Application)
3. Configure the allowed URLs:
   - **Allowed Callback URLs**: `http://localhost:3000/callback`
   - **Allowed Logout URLs**: `http://localhost:3000`
   - **Allowed Web Origins**: `http://localhost:3000`
4. Create an API with the identifier `https://linguify-api`
5. Use the generated credentials to fill in the `.env` files

## Installation Verification

1. Visit the Django admin panel: `http://localhost:8081/admin/`
2. Visit the frontend application: `http://localhost:3000`
3. Test authentication and check that the backend and frontend communicate properly

## Troubleshooting Common Issues

- **CORS Errors**: Make sure `CORS_ALLOWED_ORIGINS` in `settings.py` includes `http://localhost:3000`
- **Authentication Issues**: Ensure Auth0 redirect URLs are correctly configured
- **Database Errors**: Double-check the connection information in your `.env` file

If you run into any problems, feel free to check the documentation or open an issue on the GitHub repository.

---

Let me know if you want a version formatted for markdown documentation or a README file!