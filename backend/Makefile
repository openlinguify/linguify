# Makefile for Linguify Backend Development
# Complete application and database management

.PHONY: help install run clean apps apps-manifests app-hide app-show app-order app-delete sync-manifests st test-prod test-dev sync-prod sync-app setup-db migrate reset-db deploy-prod deploy check-deploy env env-dev env-prod

# ==============================================================================
# 🎯 HELP & INFORMATION
# ==============================================================================

help:
	@echo "🚀 LINGUIFY BACKEND - COMPLETE COMMANDS"
	@echo "========================================"
	@echo ""
	@echo "📋 DETAILED HELP:"
	@echo "  help-apps        Application management: status, visibility, sync, deletion"
	@echo "  help-db          Database management: status, sync, config, migrations"  
	@echo "  help-dev         Development: server, tests, code formatting, cleanup"
	@echo "  help-deploy      Deployment: production, validation, comparisons, workflow"
	@echo ""
	@echo "⚡ QUICK COMMANDS:"
	@echo "  st               Quick status (dev + prod)"
	@echo "  apps             List applications"
	@echo "  env              Show current environment"
	@echo "  env-dev          Switch to DEVELOPMENT"
	@echo "  env-prod         ⚠️  Switch to PRODUCTION"
	@echo "  run              Start development server"
	@echo "  test             Run tests"
	@echo ""
	@echo "🔧 INITIAL SETUP:"
	@echo "  setup            Complete initial configuration"
	@echo "  setup-db         PostgreSQL configuration only"

# ==============================================================================
# 📱 APPLICATION MANAGEMENT
# ==============================================================================

help-apps:
	@echo "📱 APPLICATION MANAGEMENT"
	@echo "========================="
	@echo ""
	@echo "📋 Status and information:"
	@echo "  apps                     List all applications"
	@echo "  apps-manifests          List found manifests"
	@echo "  app-info APP=<code>     Detailed app info"
	@echo ""
	@echo "👁️  Visibility:"
	@echo "  app-hide APP=<code>     Hide app from users"
	@echo "  app-show APP=<code>     Make app visible"
	@echo "  app-order APP=<code> ORDER=<num>  Change display order"
	@echo ""
	@echo "🔄 Synchronization:"
	@echo "  sync-app APP=<code>     Sync app to production"
	@echo "  sync-manifests          Sync all manifests"
	@echo "  sync-icons              Sync icons from manifests"
	@echo "  apply-manifests         Apply visibility per manifests"
	@echo ""
	@echo "🗑️  Cleanup:"
	@echo "  app-delete APP=<code>   Permanently delete app"
	@echo ""
	@echo "📝 Examples:"
	@echo "  make apps"
	@echo "  make app-hide APP=demo_app_test"
	@echo "  make app-show APP=community"
	@echo "  make sync-app APP=course"
	@echo "  make sync-icons"

apps:
	@echo "📱 Listing applications..."
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py list

apps-manifests:
	@echo "📋 Application manifests..."
	poetry run python scripts/database/manifest_manager.py list

app-hide:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make app-hide APP=<code>"; \
		echo "📝 Example: make app-hide APP=demo_app_test"; \
		exit 1; \
	fi
	@echo "👁️  Hiding application: $(APP)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py hide $(APP)

app-show:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make app-show APP=<code>"; \
		echo "📝 Example: make app-show APP=community"; \
		exit 1; \
	fi
	@echo "👁️  Showing application: $(APP)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py show $(APP)

app-order:
	@if [ -z "$(APP)" ] || [ -z "$(ORDER)" ]; then \
		echo "❌ Usage: make app-order APP=<code> ORDER=<number>"; \
		echo "📝 Example: make app-order APP=course ORDER=1"; \
		exit 1; \
	fi
	@echo "📊 Changing order: $(APP) → position $(ORDER)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py order $(APP) $(ORDER)

app-delete:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make app-delete APP=<code>"; \
		echo "📝 Example: make app-delete APP=demo_app_test"; \
		exit 1; \
	fi
	@echo "🗑️  Deleting application: $(APP)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py delete $(APP)

sync-manifests:
	@echo "🔄 Complete manifest synchronization..."
	@echo "   📱 Syncing app metadata"
	@echo "   🎨 Syncing icons from static/description/"
	@echo "   💾 Updating database"
	@echo ""
	@poetry run python manage.py sync_manifests
	@echo ""
	@echo "✅ Manifests synchronized!"

sync-icons:
	@echo "🎨 Synchronizing application icons..."
	@echo "   📖 Reading app manifests (__manifest__.py)"
	@echo "   🔍 Searching icons in static/description/"
	@echo "   💾 Updating database with icon info"
	@echo "   🎯 Converting categories to appropriate Bootstrap icons"
	@echo ""
	@poetry run python manage.py sync_app_icons
	@echo ""
	@echo "✅ Icons synchronized! Restart server to see changes."

apply-manifests:
	@echo "🔧 Applying manifests per environment..."
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/manifest_manager.py apply-manifest

# ==============================================================================
# 🗄️ DATABASE MANAGEMENT  
# ==============================================================================

help-db:
	@echo "🗄️  DATABASE MANAGEMENT"
	@echo "==================="
	@echo ""
	@echo "📊 Status:"
	@echo "  st               Quick status (dev + prod)"
	@echo "  status           Detailed status with comparisons"
	@echo "  test-prod        Test production connection"
	@echo "  test-dev         Test development connection"
	@echo ""
	@echo "🔄 Synchronization:"
	@echo "  sync-prod        Production → Development (complete)"
	@echo "  sync-app APP=X   Sync specific app"
	@echo ""
	@echo "⚙️  Configuration:"
	@echo "  setup-db         Configure local PostgreSQL"
	@echo "  migrate          Run migrations"
	@echo "  reset-db         Reset local DB"
	@echo ""
	@echo "📱 Test apps:"
	@echo "  quizz, course, notebook, revision, language_ai"
	@echo ""
	@echo "📝 OpenLinguify Blog:"
	@echo "  blog-articles              Create SEO articles (dev)"
	@echo "  blog-dev / blog-prod       Article status by environment"
	@echo "  blog-sync-prod             Sync dev → prod (complete)"
	@echo "  blog-sync-prod-all         Sync by model (category→tag→blogpost)"
	@echo ""
	@echo "🔄 Granular synchronization:"
	@echo "  make blog blogpost prod         Sync a table (short format)"
	@echo "  make blog-sync-table TABLE=category TARGET=prod"
	@echo "  make course-sync-table TABLE=lesson TARGET=prod"

st:
	@echo "⚡ QUICK STATUS"
	@echo "============="
	@echo ""
	@echo "🚀 Testing production with demo_app_test:"
	@if make sync-app APP=demo_app_test 2>/dev/null | grep -q "Production: ✅ Disponible"; then \
		echo "   ✅ Production connected"; \
		echo "   📱 Visible apps: $(shell make apps 2>/dev/null | grep -c '✅ Visible')"; \
		echo "   📱 Hidden apps: $(shell make apps 2>/dev/null | grep -c '❌ Cachée')"; \
	else \
		echo "   ❌ Production unavailable"; \
	fi
	@echo ""
	@echo "🏗️  Development:"
	@if make sync-app APP=demo_app_test 2>/dev/null | grep -q "Développement: ✅ Disponible"; then \
		echo "   ✅ Development connected"; \
	else \
		echo "   ❌ Local PostgreSQL not configured"; \
		echo "   💡 To configure: make setup-db"; \
	fi
	@echo ""
	@echo "🛠️  Quick actions:"
	@echo "   make apps              # List apps"
	@echo "   make app-hide APP=X    # Hide an app"  
	@echo "   make sync-app APP=X    # Sync to prod"

test-prod:
	@echo "🚀 Testing production connection..."
	@make sync-app APP=demo_app_test | head -3

test-dev:
	@echo "🏗️  Testing development connection..."
	@if make sync-app APP=demo_app_test 2>/dev/null | grep -q "Développement: ✅ Disponible"; then \
		echo "✅ Development connected"; \
	else \
		echo "❌ Development unavailable"; \
		echo "💡 Configuration: make setup-db"; \
	fi

sync-prod:
	@echo "🔄 Synchronizing Production → Development..."
	poetry run python scripts/database/sync_prod_to_dev.py

sync-app:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make sync-app APP=<code>"; \
		echo "📝 Example: make sync-app APP=course"; \
		exit 1; \
	fi
	@echo "🔄 Synchronizing app: $(APP)"
	poetry run python scripts/database/hybrid_sync_app.py $(APP)

setup-db:
	@echo "🗄️  Configuring PostgreSQL..."
	bash scripts/database/setup_postgresql.sh

migrate:
	@echo "🗄️  Running database migrations..."
	poetry run python manage.py migrate

reset-db:
	@echo "🗄️  Resetting local database..."
	poetry run python scripts/database/clean_database.py

# ==============================================================================
# 📝 BLOG MANAGEMENT & TABLE SYNC
# ==============================================================================

# Blog Management
blog-articles:
	@echo "📝 Creating OpenLinguify SEO articles (blog dev → articles + categories + tags)..."
	poetry run python manage.py create_seo_articles

blog-sync-prod:
	@echo "🔄 Complete blog synchronization to production..."
	poetry run python scripts/database/sync_blog_simple.py

blog-dev:
	@echo "🏗️  Blog articles in development..."
	@poetry run python manage.py shell -c "from core.blog.models import BlogPost, Category, Tag; print(f'📄 Articles: {BlogPost.objects.count()}'); print(f'📂 Categories: {Category.objects.count()}'); print(f'🏷️  Tags: {Tag.objects.count()}')"

blog-prod:
	@echo "🚀 Blog articles in production..."
	@DJANGO_ENV=production poetry run python manage.py shell -c "from core.blog.models import BlogPost, Category, Tag; print(f'📄 Articles: {BlogPost.objects.count()}'); print(f'📂 Categories: {Category.objects.count()}'); print(f'🏷️  Tags: {Tag.objects.count()}')"

# Table Synchronization (format: make <app>-sync-table TABLE=<table> TARGET=<env>)
%-sync-table:
	@if [ -z "$(TABLE)" ] || [ -z "$(TARGET)" ]; then \
		echo "❌ Usage: make <app>-sync-table TABLE=<table> TARGET=<env>"; \
		echo "📝 Examples:"; \
		echo "  make blog-sync-table TABLE=blogpost TARGET=prod"; \
		echo "  make blog-sync-table TABLE=category TARGET=prod"; \
		echo "  make course-sync-table TABLE=lesson TARGET=prod"; \
		exit 1; \
	fi
	@$(eval APP := $(word 1,$(subst -, ,$*)))
	@echo "🔄 Synchronizing $(APP).$(TABLE) → $(TARGET)"
	@poetry run python scripts/database/sync_table_simple.py $(APP) $(TABLE) $(TARGET)

# Shorthand syntax (format: make blog blogpost prod)
%:
	@if [ "$(words $(MAKECMDGOALS))" = "3" ]; then \
		$(eval APP := $(word 1,$(MAKECMDGOALS))) \
		$(eval TABLE := $(word 2,$(MAKECMDGOALS))) \
		$(eval TARGET := $(word 3,$(MAKECMDGOALS))) \
		echo "🔄 Synchronizing $(APP).$(TABLE) → $(TARGET)"; \
		poetry run python scripts/database/sync_table_simple.py $(APP) $(TABLE) $(TARGET); \
	else \
		echo "❌ Unrecognized format. Use:"; \
		echo "  make <app> <table> <target>    # Example: make blog blogpost prod"; \
		echo "  make <app>-sync-table TABLE=<table> TARGET=<env>"; \
	fi

# App-specific sync shortcuts
blog-sync-prod-all:
	@echo "🔄 Complete blog synchronization (all models)..."
	@make blog-sync-table TABLE=category TARGET=prod
	@make blog-sync-table TABLE=tag TARGET=prod
	@make blog-sync-table TABLE=blogpost TARGET=prod
	@echo "✅ Blog completely synchronized"

course-sync-prod-all:
	@echo "🔄 Complete course synchronization (main models)..."
	@make course-sync-table TABLE=unit TARGET=prod
	@make course-sync-table TABLE=lesson TARGET=prod
	@make course-sync-table TABLE=vocabularylist TARGET=prod
	@echo "✅ Course completely synchronized"

# ==============================================================================
# 🚀 DEPLOYMENT
# ==============================================================================

help-deploy:
	@echo "🚀 DEPLOYMENT AND PRODUCTION"
	@echo "=========================="
	@echo ""
	@echo "🎯 Interactive deployment:"
	@echo "  deploy-prod      Complete interactive menu"
	@echo "  deploy-apps      Deploy apps only"
	@echo "  deploy-content   Deploy content only"
	@echo ""
	@echo "⚡ Quick deployment:"
	@echo "  deploy APP=<code>        Deploy specific app"
	@echo "  deploy-visible           Deploy all visible apps"
	@echo ""
	@echo "🔍 Pre-deployment validation:"
	@echo "  check-deploy     Check what can be deployed"
	@echo "  diff-prod        Compare dev vs prod"
	@echo ""
	@echo "📝 Recommended workflow:"
	@echo "  1. make check-deploy     # Check differences"
	@echo "  2. make deploy APP=X     # Deploy an app"
	@echo "  3. make app-hide APP=X   # Hide if not ready"
	@echo "  4. make app-show APP=X   # Show when ready"

deploy-prod:
	@echo "🚀 Interactive deployment to production..."
	poetry run python scripts/database/deploy_to_production.py

deploy:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make deploy APP=<code>"; \
		echo "📝 Example: make deploy APP=course"; \
		exit 1; \
	fi
	@echo "🚀 Quick deployment: $(APP)"
	@make sync-app APP=$(APP)
	@echo "✅ App $(APP) deployed"
	@echo "💡 To make it visible: make app-show APP=$(APP)"

check-deploy:
	@echo "🔍 Checking deployable items..."
	@echo "📱 Hidden apps that could be deployed:"
	@make apps | grep "❌ Cachée" || echo "   No hidden apps"
	@echo ""
	@echo "💡 To deploy: make deploy APP=<code>"
	@echo "💡 To make visible: make app-show APP=<code>"

# ==============================================================================
# ⚡ DEVELOPMENT
# ==============================================================================

env:
	@echo "🔍 Current environment:"
	@poetry run python scripts/check_env.py

env-dev:
	@echo "🏗️  Switching to DEVELOPMENT mode..."
	@sed -i 's/DJANGO_ENV="production"/DJANGO_ENV="development"/' .env
	@echo "✅ Environment changed: DEVELOPMENT"
	@echo "   Database: Local PostgreSQL (localhost)"
	@make env

env-prod:
	@echo "🚀 Switching to PRODUCTION mode..."
	@echo "⚠️  WARNING: You will be working on the PRODUCTION database!"
	@read -p "Are you sure? (type 'yes' to confirm): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		sed -i 's/DJANGO_ENV="development"/DJANGO_ENV="production"/' .env; \
		echo "✅ Environment changed: PRODUCTION"; \
		echo "   Database: Supabase"; \
		make env; \
	else \
		echo "❌ Change cancelled"; \
	fi

help-dev:
	@echo "⚡ DEVELOPMENT"
	@echo "============"
	@echo ""
	@echo "🏃 Server:"
	@echo "  run              Start Django server"
	@echo "  shell            Open Django shell"
	@echo "  admin            Create superuser"
	@echo ""
	@echo "🧪 Tests:"
	@echo "  test             All tests"
	@echo "  test-fast        Quick tests (no setup)"
	@echo "  test-app APP=X   Specific app tests"
	@echo "  test-revision	  Complete revision test suite"
	@echo "  test-system      System tests"
	@echo ""
	@echo "🎨 Code:"
	@echo "  lint             Check code"
	@echo "  format           Format code"
	@echo "  check            Django checks"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  clean            Clean temporary files"

install:
	@echo "📦 Installing dependencies..."
	poetry install

run:
	@echo "🚀 Starting Django server..."
	poetry run python manage.py runserver 0.0.0.0:8000

shell:
	@echo "🐚 Opening Django shell..."
	poetry run python manage.py shell

admin:
	@echo "👤 Creating superuser..."
	poetry run python manage.py createsuperuser

test:
	@echo "🧪 Running base tests..."
	@echo "ℹ️  Selective tests to avoid configuration conflicts"
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test tests --verbosity=2

test-fast:
	@echo "🧪 Quick tests (Django check only)..."
	poetry run python manage.py check

test-app:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make test-app APP=<app_name>"; \
		echo "📝 Example: make test-app APP=notebook"; \
		exit 1; \
	fi
	@echo "🧪 Testing app: $(APP)"
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.$(APP) --verbosity=2

test-revision:
	@echo "🧪 Running revision tests"
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_integration --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_learning_edge_cases --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_learning_integration --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_learning_settings --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_learning_viewsets --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_models --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_permissions --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_serializers --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_simple --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_tags --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_views_api --verbosity=2
	@echo ""
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.revision.tests.test_settings --verbosity=2
	@echo ""
	@echo "✅ Tests Revision App are finished!"

test-system:
	@echo "🧪 System tests (public_web)..."
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test tests.test_public_web_views --verbosity=2

lint:
	@echo "🔍 Checking code..."
	poetry run flake8 . --count --show-source --statistics

format:
	@echo "🎨 Formatting code..."
	poetry run black . --line-length=120
	poetry run isort . --profile black

check:
	@echo "🔧 Django checks..."
	poetry run python manage.py check

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

# ==============================================================================
# 🎯 SETUP & CONFIGURATION
# ==============================================================================

setup:
	@echo "🎯 COMPLETE LINGUIFY CONFIGURATION"
	@echo "================================="
	@echo ""
	@echo "1️⃣ Installing dependencies..."
	@make install
	@echo ""
	@echo "2️⃣ Configuring PostgreSQL..."
	@make setup-db
	@echo ""
	@echo "3️⃣ Running migrations..."
	@make migrate
	@echo ""
	@echo "4️⃣ Syncing from production..."
	@make sync-prod
	@echo ""
	@echo "5️⃣ Syncing manifests..."
	@make sync-manifests
	@echo ""
	@echo "6️⃣ Syncing icons..."
	@make sync-icons
	@echo ""
	@echo "✅ CONFIGURATION COMPLETE!"
	@echo ""
	@echo "🎯 Next steps:"
	@echo "  make admin       # Create superuser"
	@echo "  make run         # Start server"
	@echo "  make st          # Check status"

# ==============================================================================
# 📋 UTILITY COMMANDS
# ==============================================================================

# Command to see all available commands
list-commands:
	@echo "📋 ALL AVAILABLE COMMANDS"
	@echo "======================"
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/://' | sort | column -t

# Command to validate configuration
validate:
	@echo "✅ CONFIGURATION VALIDATION"
	@echo "========================"
	@echo ""
	@echo "🔍 Django verification..."
	@make check
	@echo ""
	@echo "📊 Database status..."
	@make st
	@echo ""
	@echo "📱 Applications..."
	@make apps | head -5
	@echo ""
	@echo "Validation complete"