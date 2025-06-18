#!/bin/bash

# Script pour corriger et configurer le système d'apps Linguify
# Usage: ./scripts/fix-and-setup.sh

set -e

echo "🔧 Correction et configuration du système d'apps Linguify"
echo "========================================================"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "backend/manage.py" ]; then
    log_error "Ce script doit être exécuté depuis la racine du projet Linguify"
    exit 1
fi

cd backend

log_info "Activation de l'environnement virtuel..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    log_success "Environnement virtuel activé"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    log_success "Environnement virtuel activé (Windows)"
else
    log_warning "Aucun environnement virtuel trouvé, utilisation de Python système"
fi

# 1. Créer les migrations pour app_manager
log_info "Création des migrations pour app_manager..."
python manage.py makemigrations app_manager

# 2. Créer les migrations pour mangatheque
log_info "Création des migrations pour mangatheque..."
python manage.py makemigrations mangatheque

# 3. Appliquer toutes les migrations
log_info "Application de toutes les migrations..."
python manage.py migrate

# 4. Découvrir et synchroniser les applications
log_info "Synchronisation des applications depuis les manifests..."
python manage.py sync_apps --verbose

log_success "Configuration terminée avec succès !"

cd ..

echo ""
echo "🎉 Le système d'apps Linguify est maintenant configuré !"
echo "======================================================"
echo ""
echo "📝 Prochaines étapes :"
echo "1. Démarrer le serveur : cd backend && python manage.py runserver"
echo "2. Accéder à l'app store : http://localhost:3000/app-store"
echo "3. Tester les nouvelles applications"
echo ""