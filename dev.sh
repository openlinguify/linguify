#!/bin/bash

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function pour afficher les messages
log_message() {
    echo -e "${GREEN}[LINGUIFY]${NC} $1"
}

# Sauvegarde le chemin initial
BASE_DIR=$(pwd)

# Lance les deux serveurs dans des fenêtres séparées
log_message "Démarrage des serveurs..."

# Lance Django dans une nouvelle fenêtre
start "Django Server" cmd /c "cd backend && python manage.py runserver"

# Lance Next.js dans une nouvelle fenêtre
start "Next.js Server" cmd /c "cd frontend && npm run dev"

log_message "🚀 Les serveurs sont lancés dans des fenêtres séparées !"
log_message "📍 Django: http://localhost:8000"
log_message "📍 Next.js: http://localhost:3000"
log_message "Pour arrêter les serveurs, fermez les fenêtres"