# Makefile for Linguify - Managing 5 Django Projects
# Usage: make [target]

.PHONY: help portal lms backend cms docs all status clean install check-env env

# Port configuration
PORTAL_PORT = 8080
LMS_PORT = 8001
BACKEND_PORT = 8081
CMS_PORT = 8002
DOCS_PORT = 8003

# Python commands - Using backend virtual environment
BACKEND_VENV = ./backend/venv
PORTAL_VENV = ./portal/venv
LMS_VENV = ./lms/venv
CMS_VENV = ./cms/venv
DOCS_VENV = ./backend/venv

# Python for each project (with fallback to system)
BACKEND_PYTHON = cd backend && poetry run python
PORTAL_PYTHON = $(shell if [ -f $(PORTAL_VENV)/bin/python ]; then echo $(PORTAL_VENV)/bin/python; else echo python3; fi)
LMS_PYTHON = $(shell if [ -f $(LMS_VENV)/bin/python ]; then echo $(LMS_VENV)/bin/python; else echo python3; fi)
CMS_PYTHON = $(shell if [ -f $(CMS_VENV)/bin/python ]; then echo $(CMS_VENV)/bin/python; else echo python3; fi)
DOCS_PYTHON = $(shell if [ -f $(DOCS_VENV)/bin/python ]; then echo "$(PWD)/$(DOCS_VENV)/bin/python"; else echo python3; fi)

# Global variables for check-env
PYTHON = python3
PIP = pip3
VENV_PATH = $(shell if [ -d "./backend/venv" ]; then echo "./backend/venv"; elif [ -d "./portal/venv" ]; then echo "./portal/venv"; elif [ -d "./lms/venv" ]; then echo "./lms/venv"; elif [ -d "./cms/venv" ]; then echo "./cms/venv"; else echo ""; fi)

# Manage commands for each project
MANAGE_BACKEND = cd backend && poetry run python manage.py
MANAGE_PORTAL = cd portal && ./venv/bin/python manage.py  
MANAGE_LMS = cd lms && ./venv/bin/python manage.py
MANAGE_CMS = cd cms && ./venv/bin/python manage.py
MANAGE_DOCS = cd docs && $(DOCS_PYTHON) manage.py

# Colors for display
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Display this help
	@echo "$(BLUE)Linguify - Makefile$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

portal: ## Start Portal server (port 8080)
	@echo "$(BLUE)🌐 Starting Linguify Portal on port $(PORTAL_PORT)...$(NC)"
	@if lsof -Pi :$(PORTAL_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: Port $(PORTAL_PORT) is already in use!$(NC)"; \
		echo "$(YELLOW)💡 Try: make stop-portal or use another port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_PORTAL) runserver $(PORTAL_PORT)

lms: ## Start LMS server (port 8001)
	@echo "$(BLUE)🎓 Starting Linguify LMS on port $(LMS_PORT)...$(NC)"
	@if lsof -Pi :$(LMS_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: Port $(LMS_PORT) is already in use!$(NC)"; \
		echo "$(YELLOW)💡 Try: make stop-lms or use another port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_LMS) runserver $(LMS_PORT)

backend: ## Start Backend server (port 8081)
	@echo "$(BLUE)⚙️ Starting Linguify Backend...$(NC)"
	@echo "$(GREEN)🌐 Access server at: http://localhost:$(BACKEND_PORT)/$(NC)"
	@echo ""
	@if lsof -Pi :$(BACKEND_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: Port $(BACKEND_PORT) is already in use!$(NC)"; \
		echo "$(YELLOW)💡 Try: make stop-backend or use another port$(NC)"; \
		exit 1; \
	fi
	cd backend && poetry run python ../manage.py backend runserver 0.0.0.0:$(BACKEND_PORT)

cms: ## Start CMS Teachers server (port 8002)
	@echo "$(BLUE)👨‍🏫 Starting CMS Teachers...$(NC)"
	@echo "$(GREEN)🌐 Access server at: http://localhost:$(CMS_PORT)/$(NC)"
	@echo ""
	@if lsof -Pi :$(CMS_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: Port $(CMS_PORT) is already in use!$(NC)"; \
		echo "$(YELLOW)💡 Try: make stop-cms or use another port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_CMS) runserver $(CMS_PORT)

docs: ## Start Documentation (port 8003)
	@echo "$(BLUE)📖 Starting Linguify Documentation...$(NC)"
	@echo "$(GREEN)🌐 Access server at: http://localhost:$(DOCS_PORT)/$(NC)"
	@echo ""
	@if lsof -Pi :$(DOCS_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: Port $(DOCS_PORT) is already in use!$(NC)"; \
		echo "$(YELLOW)💡 Try: make stop-docs or use another port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_DOCS) runserver $(DOCS_PORT)

run: all ## Alias for 'all' - Start all 5 servers in parallel

all: ## Start all 5 servers in parallel
	@echo "$(BLUE)🚀 Starting all Linguify servers...$(NC)"
	@echo "$(YELLOW)Portal: http://127.0.0.1:$(PORTAL_PORT)$(NC)"
	@echo "$(YELLOW)LMS: http://127.0.0.1:$(LMS_PORT)$(NC)"
	@echo "$(YELLOW)Backend: http://127.0.0.1:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)CMS: http://127.0.0.1:$(CMS_PORT)$(NC)"
	@echo "$(YELLOW)Docs: http://127.0.0.1:$(DOCS_PORT)$(NC)"
	@echo "$(RED)Use Ctrl+C to stop all servers$(NC)"
	@echo "$(BLUE)⏳ Starting... (may take 30s on WSL)$(NC)"
	cd portal && ./venv/bin/python manage.py runserver $(PORTAL_PORT) --nothreading & \
	sleep 2 && cd lms && ./venv/bin/python manage.py runserver $(LMS_PORT) --nothreading & \
	sleep 2 && cd backend && poetry run python manage.py runserver 0.0.0.0:$(BACKEND_PORT) --nothreading & \
	sleep 2 && cd cms && ./venv/bin/python manage.py runserver $(CMS_PORT) --nothreading & \
	sleep 2 && $(MANAGE_DOCS) runserver $(DOCS_PORT) --nothreading & \
	wait

stop: ## Stop all Django servers
	@echo "$(RED)🛑 Stopping all Linguify servers...$(NC)"
	@pkill -f "manage.py.*runserver" || true
	@echo "$(GREEN)✅ All servers stopped$(NC)"

stop-portal: ## Stop Portal server
	@echo "$(RED)🛑 Stopping Portal server...$(NC)"
	@lsof -ti :$(PORTAL_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Portal server stopped$(NC)"

stop-lms: ## Stop LMS server
	@echo "$(RED)🛑 Stopping LMS server...$(NC)"
	@lsof -ti :$(LMS_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ LMS server stopped$(NC)"

stop-backend: ## Stop Backend server
	@echo "$(RED)🛑 Stopping Backend...$(NC)"
	@lsof -ti :$(BACKEND_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Backend server stopped$(NC)"

stop-cms: ## Stop CMS server
	@echo "$(RED)🛑 Stopping CMS...$(NC)"
	@lsof -ti :$(CMS_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ CMS server stopped$(NC)"

stop-docs: ## Stop Documentation server
	@echo "$(RED)🛑 Stopping Documentation...$(NC)"
	@lsof -ti :$(DOCS_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Documentation server stopped$(NC)"

restart: ## Restart all servers
	@make stop
	@sleep 2
	@make all

restart-backend: ## Restart Backend server
	@make stop-backend
	@sleep 1
	@make backend

restart-docs: ## Restart Documentation server
	@make stop-docs
	@sleep 1
	@make docs

status: ## Check projects status
	@echo "$(BLUE)📊 Checking projects status...$(NC)"
	@echo "$(YELLOW)Portal:$(NC)"
	@$(MANAGE_PORTAL) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Error$(NC)"
	@echo "$(YELLOW)LMS:$(NC)"
	@$(MANAGE_LMS) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Error$(NC)"
	@echo "$(YELLOW)Backend:$(NC)"
	@$(MANAGE_BACKEND) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Error$(NC)"
	@echo "$(YELLOW)Documentation:$(NC)"
	@$(MANAGE_DOCS) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Error$(NC)"

migrate: ## Apply migrations on all projects
	@echo "$(BLUE)📦 Applying migrations...$(NC)"
	@echo "$(YELLOW)Portal:$(NC)"
	$(MANAGE_PORTAL) migrate
	@echo "$(YELLOW)LMS:$(NC)"
	$(MANAGE_LMS) migrate
	@echo "$(YELLOW)Backend:$(NC)"
	$(MANAGE_BACKEND) migrate
	@echo "$(YELLOW)Documentation:$(NC)"
	$(MANAGE_DOCS) migrate

migrate-portal: ## Apply migrations on Portal only
	@echo "$(BLUE)📦 Migrating Portal...$(NC)"
	$(MANAGE_PORTAL) migrate

migrate-lms: ## Apply migrations on LMS only
	@echo "$(BLUE)📦 Migrating LMS...$(NC)"
	$(MANAGE_LMS) migrate

migrate-backend: ## Apply migrations on Backend only
	@echo "$(BLUE)📦 Migrating Backend...$(NC)"
	$(MANAGE_BACKEND) migrate

migrate-docs: ## Apply migrations on Documentation only
	@echo "$(BLUE)📦 Migrating Documentation...$(NC)"
	$(MANAGE_DOCS) migrate

shell-portal: ## Open Django shell for Portal
	@echo "$(BLUE)🐚 Django shell for Portal...$(NC)"
	$(MANAGE_PORTAL) shell

shell-lms: ## Open Django shell for LMS
	@echo "$(BLUE)🐚 Django shell for LMS...$(NC)"
	$(MANAGE_LMS) shell

shell-backend: ## Open Django shell for Backend
	@echo "$(BLUE)🐚 Django shell for Backend...$(NC)"
	$(MANAGE_BACKEND) shell

shell-docs: ## Open Django shell for Documentation
	@echo "$(BLUE)🐚 Django shell for Documentation...$(NC)"
	$(MANAGE_DOCS) shell

collectstatic: ## Collect static files for all projects
	@echo "$(BLUE)📁 Collecting static files...$(NC)"
	$(MANAGE_PORTAL) collectstatic --noinput
	$(MANAGE_LMS) collectstatic --noinput
	$(MANAGE_BACKEND) collectstatic --noinput
	$(MANAGE_DOCS) collectstatic --noinput

clean: ## Clean temporary files
	@echo "$(BLUE)🧹 Cleaning temporary files...$(NC)"
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

install: ## Install Python dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Installation completed$(NC)"

check-env: ## Check development/production environment for all projects
	@echo "$(BLUE)🔍 Checking Linguify environments...$(NC)"
	@echo ""
	@echo "$(YELLOW)📦 PORTAL (port 8080):$(NC)"
	@./portal/venv/bin/python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings'); import django; django.setup(); from django.conf import settings; print('  Mode:', 'Development' if settings.DEBUG else 'Production'); print('  Hosts:', settings.ALLOWED_HOSTS[:3])" 2>/dev/null || echo "  $(RED)❌ Configuration error$(NC)"
	@echo ""
	@echo "$(YELLOW)🎓 LMS (port 8001):$(NC)"
	@./lms/venv/bin/python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings'); import django; django.setup(); from django.conf import settings; print('  Mode:', 'Development' if settings.DEBUG else 'Production'); print('  Hosts:', settings.ALLOWED_HOSTS[:3])" 2>/dev/null || echo "  $(RED)❌ Configuration error$(NC)"
	@echo ""  
	@echo "$(YELLOW)⚙️ BACKEND (port 8081):$(NC)"
	@cd backend && poetry run python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); import django; django.setup(); from django.conf import settings; print('  Mode:', 'Development' if settings.DEBUG else 'Production'); print('  Hosts:', settings.ALLOWED_HOSTS[:3])" 2>/dev/null || echo "  $(RED)❌ Configuration error$(NC)"
	@echo ""
	@echo "$(YELLOW)👨‍🏫 CMS (port 8002):$(NC)"  
	@./cms/venv/bin/python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cms.settings'); import django; django.setup(); from django.conf import settings; print('  Mode:', 'Development' if settings.DEBUG else 'Production'); print('  Hosts:', settings.ALLOWED_HOSTS[:3])" 2>/dev/null || echo "  $(RED)❌ Configuration error$(NC)"
	@echo ""
	@echo "$(YELLOW)📖 DOCS (port 8003):$(NC)"
	@cd docs && $(DOCS_PYTHON) -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docs_site.settings'); import django; django.setup(); from django.conf import settings; print('  Mode:', 'Development' if settings.DEBUG else 'Production'); print('  Hosts:', settings.ALLOWED_HOSTS[:3])" 2>/dev/null || echo "  $(RED)❌ Configuration error$(NC)"
	@echo ""
	@echo "$(BLUE)💡 Tip: Use 'make urls' to see all service URLs$(NC)"

env: check-env ## Alias for check-env

# Development commands
dev-portal: ## Start Portal in development mode with automatic reload
	@echo "$(BLUE)🔄 Portal in development mode...$(NC)"
	$(MANAGE_PORTAL) runserver $(PORTAL_PORT) --settings=portal.settings

dev-lms: ## Start LMS in development mode with automatic reload
	@echo "$(BLUE)🔄 LMS in development mode...$(NC)"
	$(MANAGE_LMS) runserver $(LMS_PORT)

dev-backend: ## Start Backend in development mode with automatic reload
	@echo "$(BLUE)🔄 Backend in development mode...$(NC)"
	$(MANAGE_BACKEND) runserver $(BACKEND_PORT)

dev-docs: ## Start Documentation in development mode with automatic reload
	@echo "$(BLUE)🔄 Documentation in development mode...$(NC)"
	$(MANAGE_DOCS) runserver $(DOCS_PORT)

# Test commands
test: ## Run tests for all projects
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	$(MANAGE_PORTAL) test
	$(MANAGE_LMS) test
	$(MANAGE_BACKEND) test
	$(MANAGE_DOCS) test

test-portal: ## Run tests for Portal
	@echo "$(BLUE)🧪 Tests Portal...$(NC)"
	$(MANAGE_PORTAL) test

test-lms: ## Run tests for LMS
	@echo "$(BLUE)🧪 Tests LMS...$(NC)"
	$(MANAGE_LMS) test

test-backend: ## Run tests for Backend
	@echo "$(BLUE)🧪 Tests Backend...$(NC)"
	$(MANAGE_BACKEND) test

test-docs: ## Run tests for Documentation
	@echo "$(BLUE)🧪 Tests Documentation...$(NC)"
	$(MANAGE_DOCS) test

# Production commands
prod-check: ## Check configuration for production
	@echo "$(BLUE)🔍 Checking production configuration...$(NC)"
	$(MANAGE_PORTAL) check --deploy
	$(MANAGE_LMS) check --deploy
	$(MANAGE_BACKEND) check --deploy
	$(MANAGE_DOCS) check --deploy

deploy: ## Prepare all projects for production deployment
	@echo "$(BLUE)🚀 Preparing production deployment...$(NC)"
	@echo ""
	@echo "$(YELLOW)🔍 1. Checking configurations...$(NC)"
	@make prod-check || (echo "$(RED)❌ Configuration error detected$(NC)" && exit 1)
	@echo ""
	@echo "$(YELLOW)📁 2. Collecting static files...$(NC)"
	@echo "$(BLUE)  Portal...$(NC)"
	@$(MANAGE_PORTAL) collectstatic --clear --noinput
	@echo "$(BLUE)  LMS...$(NC)"  
	@$(MANAGE_LMS) collectstatic --clear --noinput
	@echo "$(BLUE)  Backend...$(NC)"
	@$(MANAGE_BACKEND) collectstatic --clear --noinput
	@echo "$(BLUE)  CMS...$(NC)"
	@$(MANAGE_CMS) collectstatic --clear --noinput
	@echo "$(BLUE)  Documentation...$(NC)"
	@$(MANAGE_DOCS) collectstatic --clear --noinput
	@echo ""
	@echo "$(YELLOW)🧪 3. Running tests...$(NC)"
	@make test || (echo "$(YELLOW)⚠️  Tests failed - continue with caution$(NC)")
	@echo ""
	@echo "$(YELLOW)🧹 4. Cleaning temporary files...$(NC)"
	@make clean
	@echo ""
	@echo "$(GREEN)✅ Deployment preparation completed!$(NC)"
	@echo "$(BLUE)💡 You can now:$(NC)"
	@echo "   - Commit your changes: $(YELLOW)git add . && git commit -m 'Prepare production deployment'$(NC)"
	@echo "   - Push to production: $(YELLOW)git push$(NC)"
	@echo "   - Or use your deployment tool (Render, Heroku, etc.)$(NC)"

deploy-quick: ## Quick deployment (no tests) - collect static files only
	@echo "$(BLUE)⚡ Quick deployment...$(NC)"
	@echo ""
	@echo "$(YELLOW)📁 Collecting static files...$(NC)"
	@echo "$(BLUE)  Portal...$(NC)"
	@$(MANAGE_PORTAL) collectstatic --clear --noinput
	@echo "$(BLUE)  Backend...$(NC)"
	@$(MANAGE_BACKEND) collectstatic --clear --noinput
	@echo ""
	@echo "$(GREEN)✅ Quick deployment completed!$(NC)"

deploy-portal: ## Prepare Portal only for deployment
	@echo "$(BLUE)🌐 Preparing Portal for deployment...$(NC)"
	@echo "$(YELLOW)Checking...$(NC)"
	@$(MANAGE_PORTAL) check --deploy
	@echo "$(YELLOW)Collecting static files...$(NC)"
	@$(MANAGE_PORTAL) collectstatic --clear --noinput
	@echo "$(GREEN)✅ Portal ready for deployment!$(NC)"

deploy-backend: ## Prepare Backend only for deployment
	@echo "$(BLUE)⚙️  Preparing Backend for deployment...$(NC)"
	@echo "$(YELLOW)Checking...$(NC)"
	@$(MANAGE_BACKEND) check --deploy
	@echo "$(YELLOW)Collecting static files...$(NC)"
	@$(MANAGE_BACKEND) collectstatic --clear --noinput
	@echo "$(GREEN)✅ Backend ready for deployment!$(NC)"

# Practical commands
urls: ## Display available URLs
	@echo "$(BLUE)🔗 Server URLs:$(NC)"
	@echo "$(YELLOW)Portal:$(NC) http://127.0.0.1:$(PORTAL_PORT)"
	@echo "$(YELLOW)LMS:$(NC) http://127.0.0.1:$(LMS_PORT)"
	@echo "$(YELLOW)Backend:$(NC) http://127.0.0.1:$(BACKEND_PORT)"
	@echo "$(YELLOW)CMS:$(NC) http://127.0.0.1:$(CMS_PORT)"
	@echo "$(YELLOW)Documentation:$(NC) http://127.0.0.1:$(DOCS_PORT)"

