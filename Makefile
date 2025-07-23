# Makefile pour Linguify - Gestion des 3 projets Django
# Usage: make [target]

.PHONY: help portal lms backend all status clean install

# Configuration des ports
PORTAL_PORT = 8080
LMS_PORT = 8001
BACKEND_PORT = 8000
CMS_PORT = 8002

# Commandes Python - Utilisation de l'environnement virtuel du backend
BACKEND_VENV = ./backend/venv
PORTAL_VENV = ./portal/venv
LMS_VENV = ./lms/venv
CMS_VENV = ./cms/venv

# Python pour chaque projet (avec fallback vers système)
BACKEND_PYTHON = cd backend && poetry run python
PORTAL_PYTHON = $(shell if [ -f $(PORTAL_VENV)/bin/python ]; then echo $(PORTAL_VENV)/bin/python; else echo python3; fi)
LMS_PYTHON = $(shell if [ -f $(LMS_VENV)/bin/python ]; then echo $(LMS_VENV)/bin/python; else echo python3; fi)
CMS_PYTHON = $(shell if [ -f $(CMS_VENV)/bin/python ]; then echo $(CMS_VENV)/bin/python; else echo python3; fi)

# Manage commands pour chaque projet
MANAGE_BACKEND = cd backend && poetry run python ../manage.py backend
MANAGE_PORTAL = cd portal && ./venv/bin/python manage.py  
MANAGE_LMS = cd lms && ./venv/bin/python manage.py
MANAGE_CMS = cd cms && ./venv/bin/python manage.py

# Couleurs pour l'affichage
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)Linguify - Makefile$(NC)"
	@echo "$(YELLOW)Commandes disponibles:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

portal: ## Lance le serveur Portal (port 8080)
	@echo "$(BLUE)🌐 Lancement du Portal Linguify sur le port $(PORTAL_PORT)...$(NC)"
	@if lsof -Pi :$(PORTAL_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Erreur: Le port $(PORTAL_PORT) est déjà utilisé!$(NC)"; \
		echo "$(YELLOW)💡 Essayez: make stop-portal ou utilisez un autre port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_PORTAL) runserver $(PORTAL_PORT)

lms: ## Lance le serveur LMS (port 8001)
	@echo "$(BLUE)🎓 Lancement du LMS Linguify sur le port $(LMS_PORT)...$(NC)"
	@if lsof -Pi :$(LMS_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Erreur: Le port $(LMS_PORT) est déjà utilisé!$(NC)"; \
		echo "$(YELLOW)💡 Essayez: make stop-lms ou utilisez un autre port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_LMS) runserver $(LMS_PORT)

backend: ## Lance le serveur Backend (port 8000)
	@echo "$(BLUE)⚙️ Lancement du Backend Linguify...$(NC)"
	@echo "$(GREEN)🌐 Accédez au serveur sur : http://localhost:$(BACKEND_PORT)/$(NC)"
	@echo ""
	@if lsof -Pi :$(BACKEND_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Erreur: Le port $(BACKEND_PORT) est déjà utilisé!$(NC)"; \
		echo "$(YELLOW)💡 Essayez: make stop-backend ou utilisez un autre port$(NC)"; \
		exit 1; \
	fi
	cd backend && poetry run python ../manage.py backend runserver 0.0.0.0:$(BACKEND_PORT)

cms: ## Lance le serveur CMS Enseignants (port 8002)
	@echo "$(BLUE)👨‍🏫 Lancement du CMS Enseignants...$(NC)"
	@echo "$(GREEN)🌐 Accédez au serveur sur : http://localhost:$(CMS_PORT)/$(NC)"
	@echo ""
	@if lsof -Pi :$(CMS_PORT) -t >/dev/null 2>&1; then \
		echo "$(RED)❌ Erreur: Le port $(CMS_PORT) est déjà utilisé!$(NC)"; \
		echo "$(YELLOW)💡 Essayez: make stop-cms ou utilisez un autre port$(NC)"; \
		exit 1; \
	fi
	$(MANAGE_CMS) runserver $(CMS_PORT)

all: ## Lance les 4 serveurs en parallèle
	@echo "$(BLUE) Lancement de tous les serveurs Linguify...$(NC)"
	@echo "$(YELLOW)Portal: http://127.0.0.1:$(PORTAL_PORT)$(NC)"
	@echo "$(YELLOW)LMS: http://127.0.0.1:$(LMS_PORT)$(NC)"
	@echo "$(YELLOW)Backend: http://127.0.0.1:$(BACKEND_PORT)$(NC)"
	@echo "$(YELLOW)CMS: http://127.0.0.1:$(CMS_PORT)$(NC)"
	@echo "$(RED)Utilisez Ctrl+C pour arrêter tous les serveurs$(NC)"
	@echo "$(BLUE)⏳ Démarrage en cours... (peut prendre 30s sur WSL)$(NC)"
	cd portal && ./venv/bin/python manage.py runserver $(PORTAL_PORT) --nothreading & \
	sleep 2 && cd lms && ./venv/bin/python manage.py runserver $(LMS_PORT) --nothreading & \
	sleep 2 && cd backend && poetry run python ../manage.py backend runserver 0.0.0.0:$(BACKEND_PORT) --nothreading & \
	sleep 2 && cd cms && ./venv/bin/python manage.py runserver $(CMS_PORT) --nothreading & \
	wait

stop: ## Arrête tous les serveurs Django
	@echo "$(RED)🛑 Arrêt de tous les serveurs Linguify...$(NC)"
	@pkill -f "manage.py.*runserver" || true
	@echo "$(GREEN)✅ Tous les serveurs sont arrêtés$(NC)"

stop-portal: ## Arrête le serveur Portal
	@echo "$(RED)🛑 Arrêt du serveur Portal...$(NC)"
	@lsof -ti :$(PORTAL_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Serveur Portal arrêté$(NC)"

stop-lms: ## Arrête le serveur LMS
	@echo "$(RED)🛑 Arrêt du serveur LMS...$(NC)"
	@lsof -ti :$(LMS_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Serveur LMS arrêté$(NC)"

stop-backend: ## Arrête le serveur Backend
	@echo "$(RED)🛑 Arrêt du serveur Backend...$(NC)"
	@lsof -ti :$(BACKEND_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Serveur Backend arrêté$(NC)"

stop-cms: ## Arrête le serveur CMS
	@echo "$(RED)🛑 Arrêt du serveur CMS...$(NC)"
	@lsof -ti :$(CMS_PORT) | xargs -r kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ Serveur CMS arrêté$(NC)"

restart: ## Redémarre tous les serveurs
	@make stop
	@sleep 2
	@make all

restart-backend: ## Redémarre le serveur Backend
	@make stop-backend
	@sleep 1
	@make backend

status: ## Vérifie le statut des projets
	@echo "$(BLUE)📊 Vérification du statut des projets...$(NC)"
	@echo "$(YELLOW)Portal:$(NC)"
	@$(MANAGE_PORTAL) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Erreur$(NC)"
	@echo "$(YELLOW)LMS:$(NC)"
	@$(MANAGE_LMS) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Erreur$(NC)"
	@echo "$(YELLOW)Backend:$(NC)"
	@$(MANAGE_BACKEND) check > /dev/null 2>&1 && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Erreur$(NC)"

migrate: ## Applique les migrations sur tous les projets
	@echo "$(BLUE)📦 Application des migrations...$(NC)"
	@echo "$(YELLOW)Portal:$(NC)"
	$(MANAGE_PORTAL) migrate
	@echo "$(YELLOW)LMS:$(NC)"
	$(MANAGE_LMS) migrate
	@echo "$(YELLOW)Backend:$(NC)"
	$(MANAGE_BACKEND) migrate

migrate-portal: ## Applique les migrations sur le Portal seulement
	@echo "$(BLUE)📦 Migration du Portal...$(NC)"
	$(MANAGE_PORTAL) migrate

migrate-lms: ## Applique les migrations sur le LMS seulement
	@echo "$(BLUE)📦 Migration du LMS...$(NC)"
	$(MANAGE_LMS) migrate

migrate-backend: ## Applique les migrations sur le Backend seulement
	@echo "$(BLUE)📦 Migration du Backend...$(NC)"
	$(MANAGE_BACKEND) migrate

shell-portal: ## Ouvre le shell Django pour le Portal
	@echo "$(BLUE)🐚 Shell Django Portal...$(NC)"
	$(MANAGE_PORTAL) shell

shell-lms: ## Ouvre le shell Django pour le LMS
	@echo "$(BLUE)🐚 Shell Django LMS...$(NC)"
	$(MANAGE_LMS) shell

shell-backend: ## Ouvre le shell Django pour le Backend
	@echo "$(BLUE)🐚 Shell Django Backend...$(NC)"
	$(MANAGE_BACKEND) shell

collectstatic: ## Collecte les fichiers statiques pour tous les projets
	@echo "$(BLUE)📁 Collecte des fichiers statiques...$(NC)"
	$(MANAGE_PORTAL) collectstatic --noinput
	$(MANAGE_LMS) collectstatic --noinput
	$(MANAGE_BACKEND) collectstatic --noinput

clean: ## Nettoie les fichiers temporaires
	@echo "$(BLUE)🧹 Nettoyage des fichiers temporaires...$(NC)"
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

install: ## Installe les dépendances Python
	@echo "$(BLUE)📦 Installation des dépendances...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Installation terminée$(NC)"

check-env: ## Vérifie l'environnement Python et Django
	@echo "$(BLUE)🔍 Vérification de l'environnement...$(NC)"
	@echo "$(YELLOW)Python utilisé:$(NC) $(PYTHON)"
	@echo "$(YELLOW)Version Python:$(NC)"
	@$(PYTHON) --version
	@echo "$(YELLOW)Django installé:$(NC)"
	@$(PYTHON) -c "import django; print('✅ Django', django.get_version())" || echo "$(RED)❌ Django non installé$(NC)"
	@if [ -n "$(VENV_PATH)" ]; then echo "$(GREEN)✅ Environnement virtuel détecté: $(VENV_PATH)$(NC)"; else echo "$(YELLOW)⚠️ Aucun environnement virtuel détecté$(NC)"; fi

# Commandes de développement
dev-portal: ## Lance le Portal en mode développement avec reload automatique
	@echo "$(BLUE)🔄 Portal en mode développement...$(NC)"
	$(MANAGE_PORTAL) runserver $(PORTAL_PORT) --settings=portal.settings

dev-lms: ## Lance le LMS en mode développement avec reload automatique
	@echo "$(BLUE)🔄 LMS en mode développement...$(NC)"
	$(MANAGE_LMS) runserver $(LMS_PORT)

dev-backend: ## Lance le Backend en mode développement avec reload automatique
	@echo "$(BLUE)🔄 Backend en mode développement...$(NC)"
	$(MANAGE_BACKEND) runserver $(BACKEND_PORT)

# Commandes de test
test: ## Lance les tests pour tous les projets
	@echo "$(BLUE)🧪 Lancement des tests...$(NC)"
	$(MANAGE_PORTAL) test
	$(MANAGE_LMS) test
	$(MANAGE_BACKEND) test

test-portal: ## Lance les tests pour le Portal
	@echo "$(BLUE)🧪 Tests Portal...$(NC)"
	$(MANAGE_PORTAL) test

test-lms: ## Lance les tests pour le LMS
	@echo "$(BLUE)🧪 Tests LMS...$(NC)"
	$(MANAGE_LMS) test

test-backend: ## Lance les tests pour le Backend
	@echo "$(BLUE)🧪 Tests Backend...$(NC)"
	$(MANAGE_BACKEND) test

# Commandes de production
prod-check: ## Vérifie la configuration pour la production
	@echo "$(BLUE)🔍 Vérification de la configuration de production...$(NC)"
	$(MANAGE_PORTAL) check --deploy
	$(MANAGE_LMS) check --deploy
	$(MANAGE_BACKEND) check --deploy

# Commandes pratiques
urls: ## Affiche les URLs disponibles
	@echo "$(BLUE)🔗 URLs des serveurs:$(NC)"
	@echo "$(YELLOW)Portal:$(NC) http://127.0.0.1:$(PORTAL_PORT)"
	@echo "$(YELLOW)LMS:$(NC) http://127.0.0.1:$(LMS_PORT)"
	@echo "$(YELLOW)Backend:$(NC) http://127.0.0.1:$(BACKEND_PORT)"

