# Makefile for Linguify Backend Development
# Complete application and database management

.PHONY: help install run clean apps apps-manifests app-hide app-show app-order app-delete sync-manifests st test-prod test-dev sync-prod sync-app setup-db migrate reset-db deploy-prod deploy check-deploy env env-dev env-prod

# ==============================================================================
# 🎯 HELP & INFORMATION
# ==============================================================================

help:
	@echo "🚀 LINGUIFY BACKEND - COMMANDES COMPLÈTES"
	@echo "=========================================="
	@echo ""
	@echo "📋 AIDE DÉTAILLÉE:"
	@echo "  help-apps        Gestion des applications: status, visibilité, synchronisation, suppression"
	@echo "  help-db          Gestion des bases de données: status, synchronisation, configuration, migrations"  
	@echo "  help-dev         Développement: serveur, tests, formatage de code, nettoyage"
	@echo "  help-deploy      Déploiement: production, validation, comparaisons, workflow"
	@echo ""
	@echo "⚡ COMMANDES RAPIDES:"
	@echo "  st               Status rapide (dev + prod)"
	@echo "  apps             Liste des applications"
	@echo "  env              Afficher l'environnement actuel"
	@echo "  env-dev          Passer en DÉVELOPPEMENT"
	@echo "  env-prod         ⚠️  Passer en PRODUCTION"
	@echo "  run              Démarrer le serveur de développement"
	@echo "  test             Lancer les tests"
	@echo ""
	@echo "🔧 SETUP INITIAL:"
	@echo "  setup            Configuration complète initiale"
	@echo "  setup-db         Configuration PostgreSQL uniquement"

# ==============================================================================
# 📱 APPLICATION MANAGEMENT
# ==============================================================================

help-apps:
	@echo "📱 GESTION DES APPLICATIONS"
	@echo "============================"
	@echo ""
	@echo "📋 Status et information:"
	@echo "  apps                     Liste toutes les applications"
	@echo "  apps-manifests          Liste les manifests trouvés"
	@echo "  app-info APP=<code>     Info détaillée d'une app"
	@echo ""
	@echo "👁️  Visibilité:"
	@echo "  app-hide APP=<code>     Cache une app des utilisateurs"
	@echo "  app-show APP=<code>     Rend une app visible"
	@echo "  app-order APP=<code> ORDER=<num>  Change l'ordre d'affichage"
	@echo ""
	@echo "🔄 Synchronisation:"
	@echo "  sync-app APP=<code>     Synchronise une app vers production"
	@echo "  sync-manifests          Synchronise tous les manifests"
	@echo "  sync-icons              Synchronise les icônes depuis les manifests"
	@echo "  apply-manifests         Applique la visibilité selon les manifests"
	@echo ""
	@echo "🗑️  Nettoyage:"
	@echo "  app-delete APP=<code>   Supprime définitivement une app"
	@echo ""
	@echo "📝 Exemples:"
	@echo "  make apps"
	@echo "  make app-hide APP=demo_app_test"
	@echo "  make app-show APP=community"
	@echo "  make sync-app APP=course"
	@echo "  make sync-icons"

apps:
	@echo "📱 Liste des applications..."
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py list

apps-manifests:
	@echo "📋 Manifests d'applications..."
	poetry run python scripts/database/manifest_manager.py list

app-hide:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make app-hide APP=<code>"; \
		echo "📝 Exemple: make app-hide APP=demo_app_test"; \
		exit 1; \
	fi
	@echo "👁️  Masquage de l'application: $(APP)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py hide $(APP)

app-show:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make app-show APP=<code>"; \
		echo "📝 Exemple: make app-show APP=community"; \
		exit 1; \
	fi
	@echo "👁️  Affichage de l'application: $(APP)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py show $(APP)

app-order:
	@if [ -z "$(APP)" ] || [ -z "$(ORDER)" ]; then \
		echo "❌ Usage: make app-order APP=<code> ORDER=<number>"; \
		echo "📝 Exemple: make app-order APP=course ORDER=1"; \
		exit 1; \
	fi
	@echo "📊 Changement d'ordre: $(APP) → position $(ORDER)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py order $(APP) $(ORDER)

app-delete:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make app-delete APP=<code>"; \
		echo "📝 Exemple: make app-delete APP=demo_app_test"; \
		exit 1; \
	fi
	@echo "🗑️  Suppression de l'application: $(APP)"
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/app_manager.py delete $(APP)

sync-manifests:
	@echo "🔄 Synchronisation complète des manifests..."
	@echo "   📱 Synchronise les métadonnées des apps"
	@echo "   🎨 Synchronise les icônes depuis static/description/"
	@echo "   💾 Met à jour la base de données"
	@echo ""
	@poetry run python manage.py sync_manifests
	@echo ""
	@echo "✅ Manifests synchronisés !"

sync-icons:
	@echo "🎨 Synchronisation des icônes d'applications..."
	@echo "   📖 Lit les manifests (__manifest__.py) des apps"
	@echo "   🔍 Cherche les icônes dans static/description/"
	@echo "   💾 Met à jour la base de données avec les infos d'icônes"
	@echo "   🎯 Convertit les catégories en icônes Bootstrap appropriées"
	@echo ""
	@poetry run python manage.py sync_app_icons
	@echo ""
	@echo "✅ Icônes synchronisées ! Redémarrez le serveur pour voir les changements."

apply-manifests:
	@echo "🔧 Application des manifests selon l'environnement..."
	@$(eval ENV_VAL := $(shell grep DJANGO_ENV .env | cut -d'=' -f2 | tr -d '"'))
	@DJANGO_ENV=$(ENV_VAL) poetry run python scripts/database/manifest_manager.py apply-manifest

# ==============================================================================
# 🗄️ DATABASE MANAGEMENT  
# ==============================================================================

help-db:
	@echo "🗄️  GESTION DES BASES DE DONNÉES"
	@echo "================================"
	@echo ""
	@echo "📊 Status:"
	@echo "  st               Status rapide (dev + prod)"
	@echo "  status           Status détaillé avec comparaisons"
	@echo "  test-prod        Test connexion production"
	@echo "  test-dev         Test connexion développement"
	@echo ""
	@echo "🔄 Synchronisation:"
	@echo "  sync-prod        Production → Développement (complet)"
	@echo "  sync-app APP=X   Synchronise une app spécifique"
	@echo ""
	@echo "⚙️  Configuration:"
	@echo "  setup-db         Configure PostgreSQL local"
	@echo "  migrate          Lance les migrations"
	@echo "  reset-db         Remet à zéro la DB locale"
	@echo ""
	@echo "📱 Apps de test:"
	@echo "  quizz, course, notebook, revision, language_ai"
	@echo ""
	@echo "📝 Blog OpenLinguify:"
	@echo "  blog-articles              Créer les articles SEO (dev)"
	@echo "  blog-dev / blog-prod       Status articles par environnement"
	@echo "  blog-sync-prod             Synchroniser dev → prod (complet)"
	@echo "  blog-sync-prod-all         Sync par modèle (category→tag→blogpost)"
	@echo ""
	@echo "🔄 Synchronisation granulaire:"
	@echo "  make blog blogpost prod         Sync une table (format court)"
	@echo "  make blog-sync-table TABLE=category TARGET=prod"
	@echo "  make course-sync-table TABLE=lesson TARGET=prod"

st:
	@echo "⚡ STATUS RAPIDE"
	@echo "================"
	@echo ""
	@echo "🚀 Test production avec demo_app_test:"
	@if make sync-app APP=demo_app_test 2>/dev/null | grep -q "Production: ✅ Disponible"; then \
		echo "   ✅ Production connectée"; \
		echo "   📱 Apps visibles: $(shell make apps 2>/dev/null | grep -c '✅ Visible')"; \
		echo "   📱 Apps cachées: $(shell make apps 2>/dev/null | grep -c '❌ Cachée')"; \
	else \
		echo "   ❌ Production indisponible"; \
	fi
	@echo ""
	@echo "🏗️  Développement:"
	@if make sync-app APP=demo_app_test 2>/dev/null | grep -q "Développement: ✅ Disponible"; then \
		echo "   ✅ Développement connecté"; \
	else \
		echo "   ❌ PostgreSQL local non configuré"; \
		echo "   💡 Pour configurer: make setup-db"; \
	fi
	@echo ""
	@echo "🛠️  Actions rapides:"
	@echo "   make apps              # Liste des apps"
	@echo "   make app-hide APP=X    # Cacher une app"  
	@echo "   make sync-app APP=X    # Sync vers prod"

test-prod:
	@echo "🚀 Test connexion production..."
	@make sync-app APP=demo_app_test | head -3

test-dev:
	@echo "🏗️  Test connexion développement..."
	@if make sync-app APP=demo_app_test 2>/dev/null | grep -q "Développement: ✅ Disponible"; then \
		echo "✅ Développement connecté"; \
	else \
		echo "❌ Développement indisponible"; \
		echo "💡 Configuration: make setup-db"; \
	fi

sync-prod:
	@echo "🔄 Synchronisation Production → Développement..."
	poetry run python scripts/database/sync_prod_to_dev.py

sync-app:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make sync-app APP=<code>"; \
		echo "📝 Exemple: make sync-app APP=course"; \
		exit 1; \
	fi
	@echo "🔄 Synchronisation de l'app: $(APP)"
	poetry run python scripts/database/hybrid_sync_app.py $(APP)

setup-db:
	@echo "🗄️  Configuration PostgreSQL..."
	bash scripts/database/setup_postgresql.sh

migrate:
	@echo "🗄️  Migrations base de données..."
	poetry run python manage.py migrate

reset-db:
	@echo "🗄️  Reset base de données locale..."
	poetry run python scripts/database/clean_database.py

# ==============================================================================
# 📝 BLOG MANAGEMENT & TABLE SYNC
# ==============================================================================

# Blog Management
blog-articles:
	@echo "📝 Création des articles SEO OpenLinguify (blog dev → articles + catégories + tags)..."
	poetry run python manage.py create_seo_articles

blog-sync-prod:
	@echo "🔄 Synchronisation complète du blog vers production..."
	poetry run python scripts/database/sync_blog_simple.py

blog-dev:
	@echo "🏗️  Articles blog en développement..."
	@poetry run python manage.py shell -c "from core.blog.models import BlogPost, Category, Tag; print(f'📄 Articles: {BlogPost.objects.count()}'); print(f'📂 Catégories: {Category.objects.count()}'); print(f'🏷️  Tags: {Tag.objects.count()}')"

blog-prod:
	@echo "🚀 Articles blog en production..."
	@DJANGO_ENV=production poetry run python manage.py shell -c "from core.blog.models import BlogPost, Category, Tag; print(f'📄 Articles: {BlogPost.objects.count()}'); print(f'📂 Catégories: {Category.objects.count()}'); print(f'🏷️  Tags: {Tag.objects.count()}')"

# Table Synchronization (format: make <app>-sync-table TABLE=<table> TARGET=<env>)
%-sync-table:
	@if [ -z "$(TABLE)" ] || [ -z "$(TARGET)" ]; then \
		echo "❌ Usage: make <app>-sync-table TABLE=<table> TARGET=<env>"; \
		echo "📝 Exemples:"; \
		echo "  make blog-sync-table TABLE=blogpost TARGET=prod"; \
		echo "  make blog-sync-table TABLE=category TARGET=prod"; \
		echo "  make course-sync-table TABLE=lesson TARGET=prod"; \
		exit 1; \
	fi
	@$(eval APP := $(word 1,$(subst -, ,$*)))
	@echo "🔄 Synchronisation $(APP).$(TABLE) → $(TARGET)"
	@poetry run python scripts/database/sync_table_simple.py $(APP) $(TABLE) $(TARGET)

# Shorthand syntax (format: make blog blogpost prod)
%:
	@if [ "$(words $(MAKECMDGOALS))" = "3" ]; then \
		$(eval APP := $(word 1,$(MAKECMDGOALS))) \
		$(eval TABLE := $(word 2,$(MAKECMDGOALS))) \
		$(eval TARGET := $(word 3,$(MAKECMDGOALS))) \
		echo "🔄 Synchronisation $(APP).$(TABLE) → $(TARGET)"; \
		poetry run python scripts/database/sync_table_simple.py $(APP) $(TABLE) $(TARGET); \
	else \
		echo "❌ Format non reconnu. Utilisez:"; \
		echo "  make <app> <table> <target>    # Exemple: make blog blogpost prod"; \
		echo "  make <app>-sync-table TABLE=<table> TARGET=<env>"; \
	fi

# App-specific sync shortcuts
blog-sync-prod-all:
	@echo "🔄 Synchronisation complète blog (tous les modèles)..."
	@make blog-sync-table TABLE=category TARGET=prod
	@make blog-sync-table TABLE=tag TARGET=prod
	@make blog-sync-table TABLE=blogpost TARGET=prod
	@echo "✅ Blog synchronisé complètement"

course-sync-prod-all:
	@echo "🔄 Synchronisation complète course (modèles principaux)..."
	@make course-sync-table TABLE=unit TARGET=prod
	@make course-sync-table TABLE=lesson TARGET=prod
	@make course-sync-table TABLE=vocabularylist TARGET=prod
	@echo "✅ Course synchronisé complètement"

# ==============================================================================
# 🚀 DEPLOYMENT
# ==============================================================================

help-deploy:
	@echo "🚀 DÉPLOIEMENT ET PRODUCTION"
	@echo "============================="
	@echo ""
	@echo "🎯 Déploiement interactif:"
	@echo "  deploy-prod      Menu interactif complet"
	@echo "  deploy-apps      Déploie seulement les apps"
	@echo "  deploy-content   Déploie seulement le contenu"
	@echo ""
	@echo "⚡ Déploiement rapide:"
	@echo "  deploy APP=<code>        Déploie une app spécifique"
	@echo "  deploy-visible           Déploie toutes les apps visibles"
	@echo ""
	@echo "🔍 Validation avant déploiement:"
	@echo "  check-deploy     Vérifie ce qui peut être déployé"
	@echo "  diff-prod        Compare dev vs prod"
	@echo ""
	@echo "📝 Workflow recommandé:"
	@echo "  1. make check-deploy     # Vérifier les différences"
	@echo "  2. make deploy APP=X     # Déployer une app"
	@echo "  3. make app-hide APP=X   # Cacher si pas prête"
	@echo "  4. make app-show APP=X   # Montrer quand prête"

deploy-prod:
	@echo "🚀 Déploiement interactif vers production..."
	poetry run python scripts/database/deploy_to_production.py

deploy:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make deploy APP=<code>"; \
		echo "📝 Exemple: make deploy APP=course"; \
		exit 1; \
	fi
	@echo "🚀 Déploiement rapide: $(APP)"
	@make sync-app APP=$(APP)
	@echo "✅ App $(APP) déployée"
	@echo "💡 Pour la rendre visible: make app-show APP=$(APP)"

check-deploy:
	@echo "🔍 Vérification des éléments à déployer..."
	@echo "📱 Apps cachées qui pourraient être déployées:"
	@make apps | grep "❌ Cachée" || echo "   Aucune app cachée"
	@echo ""
	@echo "💡 Pour déployer: make deploy APP=<code>"
	@echo "💡 Pour rendre visible: make app-show APP=<code>"

# ==============================================================================
# ⚡ DEVELOPMENT
# ==============================================================================

env:
	@echo "🔍 Environnement actuel:"
	@poetry run python scripts/check_env.py

env-dev:
	@echo "🏗️  Passage en mode DÉVELOPPEMENT..."
	@sed -i 's/DJANGO_ENV="production"/DJANGO_ENV="development"/' .env
	@echo "✅ Environnement changé : DÉVELOPPEMENT"
	@echo "   Base de données : PostgreSQL local (localhost)"
	@make env

env-prod:
	@echo "🚀 Passage en mode PRODUCTION..."
	@echo "⚠️  ATTENTION : Vous allez travailler sur la base de PRODUCTION !"
	@read -p "Êtes-vous sûr ? (tapez 'oui' pour confirmer) : " confirm; \
	if [ "$$confirm" = "oui" ]; then \
		sed -i 's/DJANGO_ENV="development"/DJANGO_ENV="production"/' .env; \
		echo "✅ Environnement changé : PRODUCTION"; \
		echo "   Base de données : Supabase"; \
		make env; \
	else \
		echo "❌ Changement annulé"; \
	fi

help-dev:
	@echo "⚡ DÉVELOPPEMENT"
	@echo "==============="
	@echo ""
	@echo "🏃 Serveur:"
	@echo "  run              Démarre le serveur Django"
	@echo "  shell            Ouvre le shell Django"
	@echo "  admin            Crée un superuser"
	@echo ""
	@echo "🧪 Tests:"
	@echo "  test             Tous les tests"
	@echo "  test-fast        Tests rapides (sans setup)"
	@echo "  test-app APP=X   Tests d'une app spécifique"
	@echo "  test-core        Tests du core uniquement"
	@echo ""
	@echo "🎨 Code:"
	@echo "  lint             Vérifie le code"
	@echo "  format           Formate le code"
	@echo "  check            Vérifications Django"
	@echo ""
	@echo "🧹 Nettoyage:"
	@echo "  clean            Nettoie les fichiers temporaires"

install:
	@echo "📦 Installation des dépendances..."
	poetry install

run:
	@echo "🚀 Démarrage du serveur Django..."
	poetry run python manage.py runserver

shell:
	@echo "🐚 Ouverture du shell Django..."
	poetry run python manage.py shell

admin:
	@echo "👤 Création d'un superuser..."
	poetry run python manage.py createsuperuser

test:
	@echo "🧪 Lancement des tests de base..."
	@echo "ℹ️  Tests sélectifs pour éviter les conflits de configuration"
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test tests --verbosity=2

test-fast:
	@echo "🧪 Tests rapides (check Django uniquement)..."
	poetry run python manage.py check

test-app:
	@if [ -z "$(APP)" ]; then \
		echo "❌ Usage: make test-app APP=<app_name>"; \
		echo "📝 Exemple: make test-app APP=notebook"; \
		exit 1; \
	fi
	@echo "🧪 Tests de l'app: $(APP)"
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test apps.$(APP) --verbosity=2

test-system:
	@echo "🧪 Tests système (public_web)..."
	@DJANGO_SETTINGS_MODULE=core.settings_test poetry run python manage.py test tests.test_public_web_views --verbosity=2

lint:
	@echo "🔍 Vérification du code..."
	poetry run flake8 . --count --show-source --statistics

format:
	@echo "🎨 Formatage du code..."
	poetry run black . --line-length=120
	poetry run isort . --profile black

check:
	@echo "🔧 Vérifications Django..."
	poetry run python manage.py check

clean:
	@echo "🧹 Nettoyage des fichiers temporaires..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

# ==============================================================================
# 🎯 SETUP & CONFIGURATION
# ==============================================================================

setup:
	@echo "🎯 CONFIGURATION COMPLÈTE LINGUIFY"
	@echo "=================================="
	@echo ""
	@echo "1️⃣ Installation des dépendances..."
	@make install
	@echo ""
	@echo "2️⃣ Configuration PostgreSQL..."
	@make setup-db
	@echo ""
	@echo "3️⃣ Migrations..."
	@make migrate
	@echo ""
	@echo "4️⃣ Synchronisation depuis production..."
	@make sync-prod
	@echo ""
	@echo "5️⃣ Synchronisation des manifests..."
	@make sync-manifests
	@echo ""
	@echo "6️⃣ Synchronisation des icônes..."
	@make sync-icons
	@echo ""
	@echo "✅ CONFIGURATION TERMINÉE!"
	@echo ""
	@echo "🎯 Prochaines étapes:"
	@echo "  make admin       # Créer un superuser"
	@echo "  make run         # Démarrer le serveur"
	@echo "  make st          # Vérifier le status"

# ==============================================================================
# 📋 UTILITY COMMANDS
# ==============================================================================

# Commande pour voir toutes les commandes disponibles
list-commands:
	@echo "📋 TOUTES LES COMMANDES DISPONIBLES"
	@echo "==================================="
	@grep -E '^[a-zA-Z_-]+:' Makefile | sed 's/://' | sort | column -t

# Commande pour valider la configuration
validate:
	@echo "✅ VALIDATION DE LA CONFIGURATION"
	@echo "================================="
	@echo ""
	@echo "🔍 Vérification Django..."
	@make check
	@echo ""
	@echo "📊 Status bases de données..."
	@make st
	@echo ""
	@echo "📱 Applications..."
	@make apps | head -5
	@echo ""
	@echo "✅ Validation terminée"