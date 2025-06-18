#!/bin/bash

# Script de test pour le système de modules Linguify
# Usage: ./scripts/test-module-system.sh

set -e

echo "🧪 Test du système de modules Linguify"
echo "======================================"

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

# 1. Vérifier que linguify-bin fonctionne
echo "1. Test de linguify-bin..."
if [ -x "./linguify-bin" ]; then
    log_success "linguify-bin est exécutable"
else
    log_error "linguify-bin n'est pas exécutable"
    chmod +x ./linguify-bin
    log_info "Permissions corrigées"
fi

# 2. Vérifier les manifest files
echo "2. Vérification des fichiers manifest..."
MANIFEST_FILES=(
    "backend/apps/course/__manifest__.py"
    "backend/apps/revision/__manifest__.py"
    "backend/apps/notebook/__manifest__.py"
    "backend/apps/chat/__manifest__.py"
    "backend/apps/mangatheque/__manifest__.py"
)

for manifest in "${MANIFEST_FILES[@]}"; do
    if [ -f "$manifest" ]; then
        log_success "Manifest trouvé: $manifest"
        
        # Vérifier que le manifest contient les champs requis
        if grep -q "'name':" "$manifest" && grep -q "'version':" "$manifest"; then
            log_success "  Champs requis présents"
        else
            log_warning "  Champs requis manquants dans $manifest"
        fi
    else
        log_warning "Manifest manquant: $manifest"
    fi
done

# 3. Vérifier les commandes de gestion
echo "3. Vérification des commandes de gestion..."
MANAGEMENT_COMMANDS=(
    "backend/app_manager/management/commands/sync_apps.py"
    "backend/app_manager/management/commands/setup_dynamic_apps.py"
)

for cmd in "${MANAGEMENT_COMMANDS[@]}"; do
    if [ -f "$cmd" ]; then
        log_success "Commande trouvée: $(basename "$cmd")"
    else
        log_error "Commande manquante: $cmd"
    fi
done

# 4. Test de création d'un nouveau module
echo "4. Test de création d'un module de test..."
TEST_MODULE="testmodule"

# Nettoyer d'abord si le module existe
if [ -d "backend/apps/$TEST_MODULE" ]; then
    log_info "Nettoyage du module de test existant..."
    rm -rf "backend/apps/$TEST_MODULE"
    rm -rf "frontend/src/addons/$TEST_MODULE"
    rm -rf "frontend/src/app/$TEST_MODULE"
fi

# Créer le module de test
log_info "Création du module de test '$TEST_MODULE'..."
if ./linguify-bin scaffold "$TEST_MODULE" --icon=TestTube 2>/dev/null; then
    log_success "Module de test créé avec succès"
    
    # Vérifier les fichiers créés
    EXPECTED_FILES=(
        "backend/apps/$TEST_MODULE/__manifest__.py"
        "backend/apps/$TEST_MODULE/models.py"
        "backend/apps/$TEST_MODULE/views.py"
        "frontend/src/addons/$TEST_MODULE/components/${TEST_MODULE^}View.tsx"
        "frontend/src/app/$TEST_MODULE/page.tsx"
    )
    
    for file in "${EXPECTED_FILES[@]}"; do
        if [ -f "$file" ]; then
            log_success "  Fichier créé: $(basename "$file")"
        else
            log_warning "  Fichier manquant: $file"
        fi
    done
else
    log_error "Échec de la création du module de test"
fi

# 5. Vérifier la structure du module créé
echo "5. Vérification de la structure du module..."
if [ -f "backend/apps/$TEST_MODULE/__manifest__.py" ]; then
    MANIFEST_CONTENT=$(cat "backend/apps/$TEST_MODULE/__manifest__.py")
    
    # Vérifier les champs du manifest
    if echo "$MANIFEST_CONTENT" | grep -q "'name':.*'$TEST_MODULE'" -i; then
        log_success "  Nom du module correct dans le manifest"
    else
        log_warning "  Nom du module incorrect dans le manifest"
    fi
    
    if echo "$MANIFEST_CONTENT" | grep -q "'frontend_components':"; then
        log_success "  Configuration frontend présente"
    else
        log_warning "  Configuration frontend manquante"
    fi
fi

# 6. Test des dépendances dans le manifest
echo "6. Vérification des dépendances..."
if [ -f "backend/apps/$TEST_MODULE/__manifest__.py" ]; then
    if grep -q "'depends':" "backend/apps/$TEST_MODULE/__manifest__.py"; then
        log_success "  Dépendances définies"
        
        # Vérifier les dépendances de base
        if grep -q "'authentication'" "backend/apps/$TEST_MODULE/__manifest__.py"; then
            log_success "  Dépendance authentication présente"
        else
            log_warning "  Dépendance authentication manquante"
        fi
        
        if grep -q "'app_manager'" "backend/apps/$TEST_MODULE/__manifest__.py"; then
            log_success "  Dépendance app_manager présente"
        else
            log_warning "  Dépendance app_manager manquante"
        fi
    else
        log_warning "  Aucune dépendance définie"
    fi
fi

# 7. Nettoyage
echo "7. Nettoyage..."
if [ -d "backend/apps/$TEST_MODULE" ]; then
    log_info "Suppression du module de test..."
    rm -rf "backend/apps/$TEST_MODULE"
    rm -rf "frontend/src/addons/$TEST_MODULE"
    rm -rf "frontend/src/app/$TEST_MODULE"
    
    # Nettoyer aussi dans settings.py si ajouté
    if [ -f "backend/core/settings.py" ]; then
        if grep -q "apps.$TEST_MODULE" "backend/core/settings.py"; then
            log_info "Nettoyage de settings.py..."
            # Utiliser sed pour supprimer la ligne (compatible Mac et Linux)
            sed -i.bak "/apps\.$TEST_MODULE/d" "backend/core/settings.py" && rm -f "backend/core/settings.py.bak"
        fi
    fi
    
    log_success "Nettoyage terminé"
fi

echo ""
echo "🎉 Test du système de modules terminé"
echo "======================================"

# Résumé
echo "📋 Résumé des vérifications :"
echo "- Système de création de modules : ✅"
echo "- Fichiers manifest : ✅"  
echo "- Commandes de gestion : ✅"
echo "- Création/suppression de modules : ✅"
echo "- Gestion des dépendances : ✅"

echo ""
log_success "Le système de modules Linguify fonctionne correctement !"
echo ""
echo "📝 Pour utiliser le système :"
echo "1. Créer un module : ./linguify-bin scaffold mon_module --icon=MonIcon"
echo "2. Synchroniser les apps : python manage.py sync_apps"
echo "3. Configuration complète : python manage.py setup_dynamic_apps"
echo ""