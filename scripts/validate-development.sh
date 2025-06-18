#!/bin/bash

# Script de validation pour développement sécurisé Linguify
# Usage: ./scripts/validate-development.sh mon_module_name

set -e  # Exit on any error

MODULE_NAME="$1"
if [ -z "$MODULE_NAME" ]; then
    echo "❌ Usage: $0 <module_name>"
    echo "   Example: $0 mon_nouveau_module"
    exit 1
fi

echo "🔍 Validation du module: $MODULE_NAME"
echo "=================================="

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour logs colorés
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Vérifier que le module est dans custom/
echo "1. Vérification de l'emplacement du module..."
BACKEND_PATH="backend/apps/custom/$MODULE_NAME"
FRONTEND_PATH="frontend/src/addons/custom/$MODULE_NAME"

if [ ! -d "$BACKEND_PATH" ]; then
    log_error "Module backend non trouvé dans custom/: $BACKEND_PATH"
    exit 1
fi

if [ ! -d "$FRONTEND_PATH" ]; then
    log_warning "Module frontend non trouvé: $FRONTEND_PATH (optionnel)"
fi

log_success "Module correctement placé dans custom/"

# 2. Vérifier les fichiers obligatoires backend
echo "2. Vérification des fichiers obligatoires..."
REQUIRED_FILES=(
    "__init__.py"
    "__manifest__.py"
    "models.py"
    "views.py"
    "serializers.py"
    "urls.py"
    "admin.py"
    "tests.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$BACKEND_PATH/$file" ]; then
        log_error "Fichier manquant: $BACKEND_PATH/$file"
        exit 1
    fi
done

log_success "Tous les fichiers obligatoires présents"

# 3. Vérifier le contenu du __manifest__.py
echo "3. Vérification du manifest..."
if ! grep -q "name.*:" "$BACKEND_PATH/__manifest__.py"; then
    log_error "Manifest invalide: champ 'name' manquant"
    exit 1
fi

if ! grep -q "version.*:" "$BACKEND_PATH/__manifest__.py"; then
    log_error "Manifest invalide: champ 'version' manquant"
    exit 1
fi

log_success "Manifest valide"

# 4. Vérifier que les modèles utilisent le bon préfixe de table
echo "4. Vérification des modèles..."
if [ -f "$BACKEND_PATH/models.py" ] && [ -s "$BACKEND_PATH/models.py" ]; then
    if grep -q "class.*Model" "$BACKEND_PATH/models.py"; then
        if ! grep -q "db_table.*custom_" "$BACKEND_PATH/models.py"; then
            log_warning "Vérifiez que vos modèles utilisent le préfixe 'custom_' pour db_table"
        else
            log_success "Modèles avec bon préfixe de table"
        fi
    fi
fi

# 5. Vérifier les permissions dans les vues
echo "5. Vérification des permissions..."
if grep -q "class.*ViewSet\|class.*APIView" "$BACKEND_PATH/views.py"; then
    if ! grep -q "permission_classes.*IsAuthenticated" "$BACKEND_PATH/views.py"; then
        log_error "Permissions manquantes: utilisez IsAuthenticated dans vos vues"
        exit 1
    fi
    log_success "Permissions correctement configurées"
fi

# 6. Vérifier qu'il n'y a pas de secrets hardcodés
echo "6. Vérification des secrets..."
SECRET_PATTERNS=(
    "password.*=.*['\"]"
    "secret.*=.*['\"]"
    "api_key.*=.*['\"]"
    "token.*=.*['\"]"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i "$pattern" "$BACKEND_PATH/" 2>/dev/null; then
        log_error "Possible secret hardcodé trouvé dans le code"
        exit 1
    fi
done

log_success "Pas de secrets hardcodés détectés"

# 7. Lancer les tests backend
echo "7. Tests backend..."
cd backend
if python manage.py test "apps.custom.$MODULE_NAME" --verbosity=0 2>/dev/null; then
    log_success "Tests backend passent"
else
    log_error "Tests backend en échec"
    exit 1
fi
cd ..

# 8. Tests frontend (si existe)
if [ -d "$FRONTEND_PATH" ]; then
    echo "8. Tests frontend..."
    cd frontend
    if npm test -- --testPathPattern="$MODULE_NAME" --watchAll=false --silent 2>/dev/null; then
        log_success "Tests frontend passent"
    else
        log_warning "Tests frontend en échec ou non configurés"
    fi
    cd ..
fi

# 9. Vérifier le build frontend
echo "9. Build frontend..."
cd frontend
if npm run build >/dev/null 2>&1; then
    log_success "Build frontend réussi"
else
    log_error "Build frontend en échec"
    exit 1
fi
cd ..

# 10. Vérifier la conformité des commits
echo "10. Vérification des commits..."
LAST_COMMIT=$(git log -1 --pretty=format:"%s")
if [[ $LAST_COMMIT =~ ^(feat|fix|docs|style|refactor|test|chore)\([a-z-]+\):.+ ]]; then
    log_success "Format de commit conforme"
else
    log_warning "Format de commit non conforme aux conventions"
fi

echo ""
echo "🎉 Validation terminée avec succès pour le module: $MODULE_NAME"
echo "✅ Le module est prêt pour code review et merge"