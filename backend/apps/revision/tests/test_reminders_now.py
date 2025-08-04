#!/usr/bin/env python3
"""
Test rapide des rappels de révision
"""
import os
import sys
import django
from datetime import datetime

# Configuration Django
sys.path.insert(0, '/mnt/c/Users/louis/WebstormProjects/linguify/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.revision.services.reminder_service import RevisionReminderService

def test_reminders():
    current_time = datetime.now()
    print(f"🚀 TEST RAPPELS à {current_time.strftime('%H:%M:%S')}")
    
    # Test avec l'heure actuelle forcée
    stats = RevisionReminderService.send_daily_reminders(dry_run=False)
    
    print(f"📊 Résultats:")
    print(f"   Utilisateurs vérifiés: {stats['users_checked']}")
    print(f"   Avec paramètres: {stats['users_with_settings']}")
    print(f"   Rappels activés: {stats['users_with_reminders_enabled']}")
    print(f"   À l'heure du rappel: {stats['users_at_reminder_time']}")
    print(f"   Avec cartes à réviser: {stats['users_with_cards_due']}")
    print(f"   🔔 Notifications envoyées: {stats['notifications_sent']}")
    
    if stats['notifications_sent'] > 0:
        print("✅ Rappel envoyé avec succès !")
    else:
        print("⚠️  Aucun rappel envoyé - vérifiez l'heure configurée")

if __name__ == "__main__":
    test_reminders()