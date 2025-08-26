You're absolutely right. Let me create more specific setup instructions for the environment configuration, poetry dependency management, and PostgreSQL setup:

# 🛠️ Getting Started with Linguify

Welcome to **Linguify** — a multilingual vocabulary learning platform!  
This guide will help you set up the project locally for development and testing.

---

## 🚀 Project Overview

Linguify helps users learn and manage vocabulary in multiple languages through themed lessons, exercises, and a progressive learning path.

### Tech Stack
- **Frontend**: Next.js (React + TypeScript)
- **Backend**: Django 5 (Python 3.12+)
- **Database**: PostgreSQL
- **Authentication**: Auth0
- **Dependency Management**: Poetry
- **WebSockets**: Django Channels (for real-time features)

---

## 🧰 Prerequisites

Make sure the following tools are installed on your system:
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+
- [Poetry](https://python-poetry.org/docs/#installation)
- [pnpm](https://pnpm.io/) or npm
- Git

---

## 📦 Project Structure

```bash
linguify/
├── backend/        # Django app (API, database, auth)
│   ├── apps/       # Django application modules
│   ├── core/       # Core settings and configuration
│   └── manage.py   # Django management script
├── frontend/       # Next.js app (UI)
│   ├── src/        # Source code
│   │   ├── addons/ # Feature modules
│   │   ├── components/ # Reusable UI components
│   │   └── core/   # Core utilities and services
├── docs/           # Project documentation
└── README.md
```

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/linguify.git
cd linguify
```

### 2. Set Up PostgreSQL

```bash
# Create a new PostgreSQL database
psql -U postgres
CREATE DATABASE linguify;
CREATE USER linguify_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE linguify TO linguify_user;
\q
```

### 3. Backend Setup (Django with Poetry)

```bash
cd backend

# Install dependencies using Poetry
poetry install

# Activate the Poetry shell
poetry shell

# Set up environment variables (create .env file)
cp .env.example .env
```

Now, edit the `.env` file with your actual settings:

```env
# Django settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database configuration (PostgreSQL local)
# Development database
DEV_DB_NAME=db_linguify_dev
DEV_DB_USER=postgres
DEV_DB_PASSWORD=azerty
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

# Auth0 settings
AUTH0_DOMAIN=your-auth0-domain
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=your-api-audience

# Email settings
EMAIL_HOST=your-smtp-server
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=linguify.info@gmail.com

# Backend and Frontend URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

Then continue with database setup:

```bash
# Apply migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

API will be available at: http://localhost:8000

### 4. Frontend Setup (Next.js)

```bash
cd ../frontend

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env.local
```

Edit the `.env.local` file with your actual settings:

```env
# Base URLs
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Auth0 configuration
NEXT_PUBLIC_AUTH0_DOMAIN=your-auth0-domain
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id
NEXT_PUBLIC_AUTH0_AUDIENCE=your-api-audience
NEXT_PUBLIC_AUTH0_CALLBACK_URL=http://localhost:3000/api/auth/callback
NEXT_PUBLIC_AUTH0_LOGOUT_URL=http://localhost:3000

# Feature flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

Then start the development server:

```bash
pnpm dev
```

App will run at: http://localhost:3000

Make sure your backend is running for the app to fetch data correctly.

---

## 🧠 Managing Dependencies

### Backend (Poetry)

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Export dependencies to requirements.txt (if needed)
poetry export -f requirements.txt --output requirements.txt
```

### Frontend (pnpm)

```bash
# Add a new dependency
pnpm add package-name

# Add a development dependency
pnpm add -D package-name

# Update dependencies
pnpm update
```

---

## 🧪 Running Tests

### Backend (Django)

```bash
cd backend
poetry shell
pytest
```

### Frontend (Next.js)

```bash
cd frontend
pnpm test
```

---

## 🧠 Helpful Commands

| Task | Command |
|------|---------|
| Activate Poetry shell | `poetry shell` |
| Start backend | `python manage.py runserver` |
| Start frontend | `pnpm dev` |
| Run backend tests | `pytest` |
| Run frontend tests | `pnpm test` |
| Access Django admin | Visit `http://localhost:8000/admin/` |
| Generate migration | `python manage.py makemigrations` |
| Apply migration | `python manage.py migrate` |
| Check poetry dependencies | `poetry show --tree` |

---

## 🙌 Need Help?

If you run into any issues:
- Check our FAQ
- Open an issue
- Ask in Discussions

Thanks for contributing to Linguify! 🌍🧠💬
