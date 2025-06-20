#!/usr/bin/env python3
"""
Script simple pour vérifier les candidatures en production
Usage: python check_applications.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ.setdefault('DJANGO_ENV', 'production')
django.setup()

from core.jobs.models import JobApplication
from datetime import datetime, timedelta

def check_recent_applications():
    """Affiche les candidatures récentes"""
    
    # Candidatures des 7 derniers jours
    week_ago = datetime.now() - timedelta(days=7)
    recent_apps = JobApplication.objects.filter(
        created_at__gte=week_ago
    ).order_by('-created_at')
    
    print("=" * 60)
    print(f"📊 CANDIDATURES RÉCENTES ({recent_apps.count()} au total)")
    print("=" * 60)
    
    for app in recent_apps:
        print(f"📄 {app.full_name}")
        print(f"   Email: {app.email}")
        print(f"   Poste: {app.position.title if app.position else 'Candidature spontanée'}")
        print(f"   Date: {app.created_at.strftime('%d/%m/%Y %H:%M')}")
        if app.resume_file:
            print(f"   CV: {app.resume_file.name}")
        print(f"   Statut: {app.get_status_display()}")
        print("-" * 40)

def download_cv(application_id):
    """Télécharge un CV spécifique"""
    try:
        app = JobApplication.objects.get(id=application_id)
        if app.resume_file:
            # Logique pour télécharger le fichier
            print(f"📥 CV disponible: {app.resume_file.url}")
            return app.resume_file.url
        else:
            print("❌ Aucun CV attaché")
    except JobApplication.DoesNotExist:
        print("❌ Candidature introuvable")

if __name__ == '__main__':
    print("🔗 Connexion à la base de production...")
    try:
        check_recent_applications()
        
        # Interface interactive
        while True:
            choice = input("\n💡 Actions: [v]oir plus | [d]télécharger CV | [q]uitter: ").lower()
            
            if choice == 'q':
                break
            elif choice == 'v':
                # Afficher plus de détails
                all_apps = JobApplication.objects.all().order_by('-created_at')[:20]
                for app in all_apps:
                    print(f"{app.id}: {app.full_name} - {app.email}")
            elif choice == 'd':
                app_id = input("ID de la candidature: ")
                try:
                    download_cv(int(app_id))
                except ValueError:
                    print("❌ ID invalide")
                    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Vérifiez que vous êtes bien connecté à la production")