#!/usr/bin/env python3
"""
Debug du système de rappels automatiques
"""
import os
import sys
import django
from datetime import datetime
import traceback

# Configuration Django
sys.path.insert(0, '/mnt/c/Users/louis/WebstormProjects/linguify/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.revision.services.reminder_service import RevisionReminderService
from django.contrib.auth import get_user_model
from apps.revision.models.settings_models import RevisionSettings

def debug_reminders():
    print(f"🔍 DEBUG SYSTÈME DE RAPPELS - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Vérifier les utilisateurs et paramètres
        User = get_user_model()
        users = User.objects.all()
        print(f"👥 Utilisateurs trouvés: {users.count()}")
        
        for user in users:
            print(f"\n🔸 Utilisateur: {user.username}")
            print(f"   User.reminder_time: {user.reminder_time}")
            print(f"   User.weekday_reminders: {user.weekday_reminders}")
            
            try:
                revision_settings = RevisionSettings.objects.get(user=user)
                print(f"   RevisionSettings.reminder_time: {revision_settings.reminder_time}")
                print(f"   RevisionSettings.daily_reminder_enabled: {revision_settings.daily_reminder_enabled}")
            except RevisionSettings.DoesNotExist:
                print(f"   ❌ Pas de RevisionSettings")
        
        # Test du service
        print(f"\n🧪 TEST DU SERVICE...")
        current_time = datetime.now()
        print(f"   Heure actuelle: {current_time.strftime('%H:%M:%S')}")
        
        stats = RevisionReminderService.send_daily_reminders(dry_run=False)
        
        print(f"\n📊 RÉSULTATS:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
            
        if stats['notifications_sent'] > 0:
            print(f"\n✅ {stats['notifications_sent']} notification(s) envoyée(s) !")
        else:
            print(f"\n⚠️  Aucune notification envoyée")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        print(f"📋 Traceback complet:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_reminders()