#!/bin/bash
# Script pour démarrer les rappels automatiques
# Lance une boucle qui vérifie toutes les minutes

PROJECT_DIR="/mnt/c/Users/louis/WebstormProjects/linguify/backend"
cd "$PROJECT_DIR"

echo "🚀 Démarrage des rappels automatiques de révision..."
echo "   Logs sauvegardés dans: auto_reminders.log"

# Lancer avec poetry et rediriger les logs
poetry run python3 scripts/auto_reminder_loop.py 2>&1 | tee auto_reminders.log