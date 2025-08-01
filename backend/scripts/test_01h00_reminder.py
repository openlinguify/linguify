#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour les notifications à 01:00
Utilise le service de révision pour envoyer une notification immédiate
"""
import os
import sys
import django
from datetime import datetime

# Ajouter le répertoire du projet au Python path
sys.path.insert(0, '/mnt/c/Users/louis/WebstormProjects/linguify/backend')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.revision.services.reminder_service import RevisionReminderService
from django.contrib.auth import get_user_model

def main():
    """Test d'envoi de notification à 01:00"""
    User = get_user_model()
    
    print(f"🕐 Test de notification à {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Obtenir l'utilisateur admin
        admin_user = User.objects.get(username='admin')
        
        # Envoyer une notification immédiate
        result = RevisionReminderService.send_immediate_reminder(admin_user, force=True)
        
        if result:
            print("✅ Notification envoyée avec succès !")
        else:
            print("❌ Échec de l'envoi de la notification")
            
    except User.DoesNotExist:
        print("❌ Utilisateur admin non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()