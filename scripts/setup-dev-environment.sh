#!/bin/bash

# Script de setup pour nouvel environnement de développement Linguify
# Usage: ./scripts/setup-dev-environment.sh

set -e  # Exit on any error

echo "🚀 Configuration de l'environnement de développement Linguify"
echo "=============================================================="

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

# 1. Vérifier les prérequis
echo "1. Vérification des prérequis..."

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python installé: $PYTHON_VERSION"
else
    log_error "Python 3 non installé"
    exit 1
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_success "Node.js installé: $NODE_VERSION"
else
    log_error "Node.js non installé"
    exit 1
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    log_success "Git installé: $GIT_VERSION"
else
    log_error "Git non installé"
    exit 1
fi

# 2. Configuration Git hooks
echo "2. Configuration des Git hooks..."
mkdir -p .git/hooks

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook pour Linguify

echo "🔍 Vérification pre-commit..."

# Vérifier que les fichiers modifiés sont dans custom/ ou docs/
MODIFIED_FILES=$(git diff --cached --name-only)
CORE_FILES_MODIFIED=false

for file in $MODIFIED_FILES; do
    # Autoriser modifications dans custom/, docs/, scripts/, frontend/src/addons/custom/
    if [[ $file == backend/apps/custom/* ]] || \
       [[ $file == frontend/src/addons/custom/* ]] || \
       [[ $file == docs/* ]] || \
       [[ $file == scripts/* ]] || \
       [[ $file == *.md ]] || \
       [[ $file == linguify-bin* ]]; then
        continue
    else
        echo "❌ Modification interdite de fichier core: $file"
        echo "   Seuls les dossiers custom/, docs/, scripts/ sont autorisés"
        CORE_FILES_MODIFIED=true
    fi
done

if [ "$CORE_FILES_MODIFIED" = true ]; then
    echo "🚨 Commit bloqué: modifications de fichiers core détectées"
    echo "   Déplacez vos modifications dans custom/ ou demandez une review"
    exit 1
fi

echo "✅ Pre-commit validé"
EOF

chmod +x .git/hooks/pre-commit
log_success "Git hooks configurés"

# 3. Configuration Backend
echo "3. Configuration Backend Django..."
cd backend

# Vérifier si venv existe
if [ ! -d "venv" ]; then
    log_info "Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi

# Activer venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Installer dépendances
if [ -f "requirements.txt" ]; then
    log_info "Installation des dépendances Python..."
    pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
    log_info "Installation via Poetry..."
    pip install poetry
    poetry install
fi

# Copier .env.example si pas de .env
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    log_info "Création du fichier .env..."
    cp .env.example .env
    log_warning "Configurez votre fichier .env avec vos variables d'environnement"
fi

# Migrations
log_info "Application des migrations..."
python manage.py migrate

# Collectstatic
log_info "Collection des fichiers statiques..."
python manage.py collectstatic --noinput

log_success "Backend configuré"
cd ..

# 4. Configuration Frontend
echo "4. Configuration Frontend Next.js..."
cd frontend

# Installer dépendances
if [ -f "package.json" ]; then
    log_info "Installation des dépendances npm..."
    npm install
fi

# Configuration .env.local
if [ -f ".env.example" ] && [ ! -f ".env.local" ]; then
    log_info "Création du fichier .env.local..."
    cp .env.example .env.local
    log_warning "Configurez votre fichier .env.local"
fi

log_success "Frontend configuré"
cd ..

# 5. Configuration de l'IDE (optionnel)
echo "5. Configuration IDE..."

# VS Code settings
if command -v code &> /dev/null; then
    mkdir -p .vscode
    
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "typescript.preferences.importModuleSpecifier": "relative",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/venv": true,
        "**/.git": true
    }
}
EOF

    cat > .vscode/extensions.json << EOF
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-typescript-next"
    ]
}
EOF

    log_success "Configuration VS Code créée"
fi

# 6. Tests de validation
echo "6. Tests de validation de l'installation..."

# Test backend
cd backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
if python manage.py check; then
    log_success "Backend opérationnel"
else
    log_error "Problème avec la configuration backend"
    exit 1
fi
cd ..

# Test frontend
cd frontend
if npm run build >/dev/null 2>&1; then
    log_success "Frontend opérationnel"
else
    log_error "Problème avec la configuration frontend"
    exit 1
fi
cd ..

# 7. Création du premier module de test (optionnel)
echo "7. Souhaitez-vous créer un module de test ? (y/N)"
read -r create_test_module

if [[ $create_test_module =~ ^[Yy]$ ]]; then
    log_info "Création du module de test..."
    ./linguify-bin scaffold test_module custom
    
    # Valider le module de test
    if ./scripts/validate-development.sh test_module; then
        log_success "Module de test créé et validé"
    else
        log_warning "Module de test créé mais validation échouée"
    fi
fi

# 8. Affichage des commandes utiles
echo ""
echo "🎉 Environnement de développement configuré avec succès !"
echo "==========================================================="
echo ""
echo "📋 Commandes utiles :"
echo ""
echo "Backend :"
echo "  cd backend && source venv/bin/activate"
echo "  python manage.py runserver"
echo "  python manage.py test"
echo ""
echo "Frontend :"
echo "  cd frontend"
echo "  npm run dev"
echo "  npm test"
echo ""
echo "Développement :"
echo "  ./linguify-bin scaffold <nom_module> custom"
echo "  ./scripts/validate-development.sh <nom_module>"
echo ""
echo "📚 Documentation :"
echo "  docs/development/developer-guidelines.md"
echo "  docs/development/app-structure-template.md"
echo "  docs/development/development-rules.md"
echo ""
echo "🔗 URLs utiles :"
echo "  Backend Admin: http://localhost:8000/admin/"
echo "  Frontend: http://localhost:3000/"
echo "  API Docs: http://localhost:8000/api/docs/"
echo ""
log_success "Bon développement ! 🚀"