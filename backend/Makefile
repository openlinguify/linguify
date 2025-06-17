# Makefile for Linguify Backend Development

.PHONY: help test test-dynamic test-fast test-coverage lint format migrate run install clean

# Default target
help:
	@echo "🚀 Linguify Backend Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Development:"
	@echo "  install     Install dependencies with Poetry"
	@echo "  run         Start Django development server"
	@echo "  migrate     Run database migrations"
	@echo "  shell       Open Django shell"
	@echo ""
	@echo "Testing:"
	@echo "  test        Run all tests"
	@echo "  test-dynamic Run dynamic system tests only"
	@echo "  test-fast   Run tests with SQLite (faster)"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run code linting"
	@echo "  format      Format code"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       Clean temporary files"
	@echo "  validate-manifests Validate app manifests"

# Installation
install:
	@echo "📦 Installing dependencies..."
	poetry install

# Development server
run:
	@echo "🚀 Starting Django development server..."
	poetry run python manage.py runserver

# Database
migrate:
	@echo "🗄️ Running database migrations..."
	poetry run python manage.py migrate

shell:
	@echo "🐚 Opening Django shell..."
	poetry run python manage.py shell

# Testing
test:
	@echo "🧪 Running all tests..."
	poetry run python run_all_tests.py

test-dynamic:
	@echo "🧪 Running dynamic system tests..."
	@export DJANGO_SETTINGS_MODULE=core.settings_test && \
	poetry run python manage.py test tests.test_public_web_dynamic_system --verbosity=2 && \
	poetry run python manage.py test tests.test_public_web_views --verbosity=2 && \
	poetry run python manage.py test tests.test_public_web_templatetags --verbosity=2 && \
	poetry run python manage.py test tests.test_public_web_integration --verbosity=2

test-fast:
	@echo "🧪 Running tests with SQLite (fast)..."
	@export DJANGO_SETTINGS_MODULE=core.settings_test && \
	poetry run python manage.py test --verbosity=2

test-coverage:
	@echo "🧪 Running tests with coverage..."
	poetry run coverage run --source='.' manage.py test
	poetry run coverage report
	poetry run coverage html

# Code quality
lint:
	@echo "🔍 Running code linting..."
	poetry run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "🎨 Formatting code..."
	poetry run black . --line-length=120
	poetry run isort . --profile black

# Validation
validate-manifests:
	@echo "🔍 Validating app manifests..."
	@export DJANGO_SETTINGS_MODULE=core.settings_test && \
	poetry run python -c "
import django; django.setup()
from public_web.utils import AppManifestParser
parser = AppManifestParser()
manifests = parser.get_all_manifests()
apps = parser.get_public_apps()
print(f'✅ Found {len(manifests)} manifests, {len(apps)} public apps')
for app in apps:
    print(f'  - {app[\"name\"]} (slug: {app[\"slug\"]})')
"

# Cleanup
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/
	rm -rf .pytest_cache/
	rm -rf .tox/

# Docker commands (if needed)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t linguify-backend .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 linguify-backend

# Utility commands
check-system:
	@echo "🔧 Running Django system check..."
	poetry run python manage.py check

collect-static:
	@echo "📦 Collecting static files..."
	poetry run python manage.py collectstatic --noinput

# Development utilities
create-superuser:
	@echo "👤 Creating superuser..."
	poetry run python manage.py createsuperuser

reset-db:
	@echo "🗄️ Resetting database..."
	poetry run python manage.py flush --noinput
	poetry run python manage.py migrate

# Translation commands
make-messages:
	@echo "🌍 Creating translation messages..."
	poetry run python manage.py makemessages -l fr -l es -l nl

compile-messages:
	@echo "🌍 Compiling translation messages..."
	poetry run python manage.py compilemessages