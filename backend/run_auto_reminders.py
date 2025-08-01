#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Système automatique de rappels de révision
Lance un processus qui surveille et envoie automatiquement les notifications
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
    """Boucle de surveillance automatique"""
    print(f"🚀 SYSTÈME DE RAPPELS AUTOMATIQUE DÉMARRÉ à {datetime.now().strftime('%H:%M:%S')}")
    print("   • Vérification toutes les minutes")
    print("   • Envoi selon l'heure configurée dans l'interface")
    print("   • Appuyez sur Ctrl+C pour arrêter\n")
    
    try:
        while True:
            current_time = datetime.now()
            minute_str = current_time.strftime('%H:%M')
            
            # Envoyer les rappels quotidiens
            stats = RevisionReminderService.send_daily_reminders(dry_run=False)
            
            if stats['notifications_sent'] > 0:
                print(f"🔔 {minute_str} - ✅ {stats['notifications_sent']} notification(s) envoyée(s) !")
                print(f"    📊 Utilisateurs vérifiés: {stats['users_checked']}")
            else:
                # Affichage réduit pour éviter le spam
                if current_time.second < 5:  # Afficher seulement au début de chaque minute
                    reasons = []
                    if stats['users_checked'] == 0:
                        reasons.append("aucun utilisateur actif")
                    elif stats['users_with_settings'] == 0:
                        reasons.append("aucun paramètre de révision")
                    elif stats['users_with_reminders_enabled'] == 0:
                        reasons.append("rappels désactivés")
                    elif stats['users_at_reminder_time'] == 0:
                        reasons.append("pas l'heure du rappel")
                    elif stats['users_with_cards_due'] == 0:
                        reasons.append("aucune carte à réviser")
                    
                    reason = reasons[0] if reasons else "raison inconnue"
                    print(f"⚪ {minute_str} - Aucune notification ({reason})")
            
            # Attendre 60 secondes
            time.sleep(60)
            
    except KeyboardInterrupt:
        print(f"\n🛑 Système arrêté à {datetime.now().strftime('%H:%M:%S')}")
        print("Merci d'avoir utilisé le système de rappels automatique !")

if __name__ == "__main__":
    main()