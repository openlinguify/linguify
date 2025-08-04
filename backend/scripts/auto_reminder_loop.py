#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boucle automatique pour les rappels de révision
Vérifie toutes les minutes si des notifications doivent être envoyées
"""
import os
import sys
import time
import django
from datetime import datetime

# Configuration Django
sys.path.insert(0, '/mnt/c/Users/louis/WebstormProjects/linguify/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.revision.services.reminder_service import RevisionReminderService

def main():
    """Boucle principale de vérification"""
    print(f"🚀 Démarrage du système de rappels automatiques à {datetime.now().strftime('%H:%M:%S')}")
    print("   Vérification toutes les minutes...")
    print("   Appuyez sur Ctrl+C pour arrêter")
    
    try:
        while True:
            current_time = datetime.now()
            print(f"\n⏰ Vérification à {current_time.strftime('%H:%M:%S')}")
            
            # Envoyer les rappels quotidiens
            stats = RevisionReminderService.send_daily_reminders(dry_run=False)
            
            if stats['notifications_sent'] > 0:
                print(f"   ✅ {stats['notifications_sent']} notification(s) envoyée(s)")
            else:
                print(f"   ⚪ Aucune notification à envoyer")
                if stats['users_checked'] > 0:
                    print(f"      (Vérifié {stats['users_checked']} utilisateur(s))")
            
            # Attendre 60 secondes avant la prochaine vérification
            time.sleep(60)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Arrêt du système de rappels à {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()