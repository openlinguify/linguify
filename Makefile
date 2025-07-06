# Makefile pour Linguify - Gestion des 3 projets Django
# Usage: make [target]

.PHONY: help portal lms backend all status clean install

# Configuration des ports
PORTAL_PORT = 8080
LMS_PORT = 8001
BACKEND_PORT = 8000

# Commandes Python - Détection automatique de l'environnement virtuel
VENV_PATH = $(shell find . -name "venv" -o -name ".venv" -o -name "env" -o -name ".env" -type d | head -n1)
ifneq ($(VENV_PATH),)
	PYTHON = $(VENV_PATH)/bin/python
	PIP = $(VENV_PATH)/bin/pip
else
	PYTHON = python3
	PIP = pip3
endif
MANAGE = $(PYTHON) manage.py

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
	$(MANAGE) portal runserver $(PORTAL_PORT)

lms: ## Lance le serveur LMS (port 8001)
	@echo "$(BLUE)🎓 Lancement du LMS Linguify sur le port $(LMS_PORT)...$(NC)"
	$(MANAGE) lms runserver $(LMS_PORT)

backend: ## Lance le serveur Backend (port 8000)
	@echo "$(BLUE)⚙️ Lancement du Backend Linguify sur le port $(BACKEND_PORT)...$(NC)"
	$(MANAGE) backend runserver $(BACKEND_PORT)

all: ## Lance les 3 serveurs en parallèle
	@echo "$(BLUE)🚀 Lancement de tous les serveurs Linguify...$(NC)"
	@echo "$(YELLOW)Portal: http://127.0.0.1:$(PORTAL_PORT)$(NC)"
	@echo "$(YELLOW)LMS: http://127.0.0.1:$(LMS_PORT)$(NC)"
	@echo "$(YELLOW)Backend: http://127.0.0.1:$(BACKEND_PORT)$(NC)"
	@echo "$(RED)Utilisez Ctrl+C pour arrêter tous les serveurs$(NC)"
	$(MANAGE) portal runserver $(PORTAL_PORT) & \
	$(MANAGE) lms runserver $(LMS_PORT) & \
	$(MANAGE) backend runserver $(BACKEND_PORT) & \
	wait

status: ## Vérifie le statut des projets
	@echo "$(BLUE)📊 Vérification du statut des projets...$(NC)"
	@echo "$(YELLOW)Portal:$(NC)"
	@$(MANAGE) portal check --quiet && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Erreur$(NC)"
	@echo "$(YELLOW)LMS:$(NC)"
	@$(MANAGE) lms check --quiet && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Erreur$(NC)"
	@echo "$(YELLOW)Backend:$(NC)"
	@$(MANAGE) backend check --quiet && echo "  $(GREEN)✅ OK$(NC)" || echo "  $(RED)❌ Erreur$(NC)"

migrate: ## Applique les migrations sur tous les projets
	@echo "$(BLUE)📦 Application des migrations...$(NC)"
	@echo "$(YELLOW)Portal:$(NC)"
	$(MANAGE) portal migrate
	@echo "$(YELLOW)LMS:$(NC)"
	$(MANAGE) lms migrate
	@echo "$(YELLOW)Backend:$(NC)"
	$(MANAGE) backend migrate

migrate-portal: ## Applique les migrations sur le Portal seulement
	@echo "$(BLUE)📦 Migration du Portal...$(NC)"
	$(MANAGE) portal migrate

migrate-lms: ## Applique les migrations sur le LMS seulement
	@echo "$(BLUE)📦 Migration du LMS...$(NC)"
	$(MANAGE) lms migrate

migrate-backend: ## Applique les migrations sur le Backend seulement
	@echo "$(BLUE)📦 Migration du Backend...$(NC)"
	$(MANAGE) backend migrate

shell-portal: ## Ouvre le shell Django pour le Portal
	@echo "$(BLUE)🐚 Shell Django Portal...$(NC)"
	$(MANAGE) portal shell

shell-lms: ## Ouvre le shell Django pour le LMS
	@echo "$(BLUE)🐚 Shell Django LMS...$(NC)"
	$(MANAGE) lms shell

shell-backend: ## Ouvre le shell Django pour le Backend
	@echo "$(BLUE)🐚 Shell Django Backend...$(NC)"
	$(MANAGE) backend shell

collectstatic: ## Collecte les fichiers statiques pour tous les projets
	@echo "$(BLUE)📁 Collecte des fichiers statiques...$(NC)"
	$(MANAGE) portal collectstatic --noinput
	$(MANAGE) lms collectstatic --noinput
	$(MANAGE) backend collectstatic --noinput

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
	$(MANAGE) portal runserver $(PORTAL_PORT) --settings=portal.settings

dev-lms: ## Lance le LMS en mode développement avec reload automatique
	@echo "$(BLUE)🔄 LMS en mode développement...$(NC)"
	$(MANAGE) lms runserver $(LMS_PORT)

dev-backend: ## Lance le Backend en mode développement avec reload automatique
	@echo "$(BLUE)🔄 Backend en mode développement...$(NC)"
	$(MANAGE) backend runserver $(BACKEND_PORT)

# Commandes de test
test: ## Lance les tests pour tous les projets
	@echo "$(BLUE)🧪 Lancement des tests...$(NC)"
	$(MANAGE) portal test
	$(MANAGE) lms test
	$(MANAGE) backend test

test-portal: ## Lance les tests pour le Portal
	@echo "$(BLUE)🧪 Tests Portal...$(NC)"
	$(MANAGE) portal test

test-lms: ## Lance les tests pour le LMS
	@echo "$(BLUE)🧪 Tests LMS...$(NC)"
	$(MANAGE) lms test

test-backend: ## Lance les tests pour le Backend
	@echo "$(BLUE)🧪 Tests Backend...$(NC)"
	$(MANAGE) backend test

# Commandes de production
prod-check: ## Vérifie la configuration pour la production
	@echo "$(BLUE)🔍 Vérification de la configuration de production...$(NC)"
	$(MANAGE) portal check --deploy
	$(MANAGE) lms check --deploy
	$(MANAGE) backend check --deploy

# Commandes pratiques
urls: ## Affiche les URLs disponibles
	@echo "$(BLUE)🔗 URLs des serveurs:$(NC)"
	@echo "$(YELLOW)Portal:$(NC) http://127.0.0.1:$(PORTAL_PORT)"
	@echo "$(YELLOW)LMS:$(NC) http://127.0.0.1:$(LMS_PORT)"
	@echo "$(YELLOW)Backend:$(NC) http://127.0.0.1:$(BACKEND_PORT)"

stop: ## Arrête tous les processus Django en cours
	@echo "$(BLUE)🛑 Arrêt des serveurs Django...$(NC)"
	@pkill -f "manage.py.*runserver" || echo "$(YELLOW)Aucun serveur à arrêter$(NC)"
	@echo "$(GREEN)✅ Serveurs arrêtés$(NC)"