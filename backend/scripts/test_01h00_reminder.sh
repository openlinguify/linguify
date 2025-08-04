#!/bin/bash
# Script de test pour notifications à 01:00

PROJECT_DIR="/mnt/c/Users/louis/WebstormProjects/linguify/backend"
cd "$PROJECT_DIR"

echo "🕐 Test de notification à $(date '+%H:%M:%S')"

# Utiliser poetry pour exécuter avec le bon environnement
poetry run python3 -c "
import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.revision.services.reminder_service import RevisionReminderService
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    admin_user = User.objects.get(username='admin')
    result = RevisionReminderService.send_immediate_reminder(admin_user, force=True)
    
    if result:
        print('✅ Notification envoyée avec succès !')
    else:
        print('❌ Échec de l\\'envoi de la notification')
        
except User.DoesNotExist:
    print('❌ Utilisateur admin non trouvé')
except Exception as e:
    print(f'❌ Erreur: {e}')
"