#!/bin/bash
# Script pour envoyer les rappels de révision
# À programmer avec cron pour exécution automatique

# Répertoire du projet
PROJECT_DIR="/mnt/c/Users/louis/WebstormProjects/linguify/backend"

# Aller dans le répertoire du projet
cd "$PROJECT_DIR"

# Enregistrer dans les logs
echo "$(date): Démarrage des rappels de révision" >> /var/log/linguify_reminders.log

# Exécuter la commande avec poetry
poetry run python manage.py send_revision_reminders >> /var/log/linguify_reminders.log 2>&1

# Enregistrer la fin
echo "$(date): Fin des rappels de révision" >> /var/log/linguify_reminders.log