#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de synchronisation sélective bidirectionnelle
Permet des synchronisations fines entre développement et production
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta
import subprocess

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.core import serializers
from django.apps import apps
from django.db import models


class SelectiveSync:
    """Gestionnaire de synchronisation sélective"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def get_new_apps_since_date(self, since_date):
        """Récupère les nouvelles applications depuis une date"""
        from app_manager.models import App
        
        new_apps = App.objects.filter(
            created_at__gte=since_date
        ).order_by('-created_at')
        
        return new_apps
        
    def get_modified_courses_since_date(self, since_date):
        """Récupère les cours modifiés depuis une date"""
        from course.models import Course, Lesson
        
        # Cours modifiés
        modified_courses = Course.objects.filter(
            updated_at__gte=since_date
        ).order_by('-updated_at')
        
        # Leçons modifiées
        modified_lessons = Lesson.objects.filter(
            updated_at__gte=since_date
        ).order_by('-updated_at')
        
        return modified_courses, modified_lessons
        
    def get_new_content_since_date(self, since_date):
        """Récupère le nouveau contenu depuis une date"""
        from course.models import TheoryContent, MatchingExercise, VocabularyList
        
        new_theory = TheoryContent.objects.filter(
            created_at__gte=since_date
        ).order_by('-created_at')
        
        new_matching = MatchingExercise.objects.filter(
            created_at__gte=since_date
        ).order_by('-created_at')
        
        new_vocabulary = VocabularyList.objects.filter(
            created_at__gte=since_date
        ).order_by('-created_at')
        
        return new_theory, new_matching, new_vocabulary
        
    def export_changes_since_date(self, since_date, direction="dev_to_prod"):
        """Exporte les changements depuis une date donnée"""
        print(f"📅 Export des changements depuis {since_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        export_data = {
            'timestamp': self.timestamp,
            'since_date': since_date.isoformat(),
            'direction': direction,
            'exported_objects': {}
        }
        
        # Nouvelles applications
        new_apps = self.get_new_apps_since_date(since_date)
        if new_apps.exists():
            filename = f"new_apps_{self.timestamp}.json"
            call_command(
                'dumpdata',
                'app_manager.App',
                '--pks', ','.join(str(app.id) for app in new_apps),
                '--format=json',
                '--indent=2',
                '--output', filename
            )
            export_data['exported_objects']['apps'] = {
                'count': new_apps.count(),
                'file': filename,
                'objects': [{'id': app.id, 'name': app.name} for app in new_apps]
            }
            print(f"  ✅ {new_apps.count()} nouvelles applications exportées")
            
        # Cours modifiés
        modified_courses, modified_lessons = self.get_modified_courses_since_date(since_date)
        if modified_courses.exists() or modified_lessons.exists():
            
            # Export des cours
            if modified_courses.exists():
                filename = f"modified_courses_{self.timestamp}.json"
                call_command(
                    'dumpdata',
                    'course.Course',
                    '--pks', ','.join(str(course.id) for course in modified_courses),
                    '--format=json',
                    '--indent=2',
                    '--output', filename
                )
                export_data['exported_objects']['courses'] = {
                    'count': modified_courses.count(),
                    'file': filename
                }
                print(f"  ✅ {modified_courses.count()} cours modifiés exportés")
                
            # Export des leçons
            if modified_lessons.exists():
                filename = f"modified_lessons_{self.timestamp}.json"
                call_command(
                    'dumpdata',
                    'course.Lesson',
                    'course.ContentLesson',
                    '--pks', ','.join(str(lesson.id) for lesson in modified_lessons),
                    '--format=json',
                    '--indent=2',
                    '--output', filename
                )
                export_data['exported_objects']['lessons'] = {
                    'count': modified_lessons.count(),
                    'file': filename
                }
                print(f"  ✅ {modified_lessons.count()} leçons modifiées exportées")
                
        # Nouveau contenu
        new_theory, new_matching, new_vocabulary = self.get_new_content_since_date(since_date)
        
        if new_theory.exists():
            filename = f"new_theory_{self.timestamp}.json"
            call_command(
                'dumpdata',
                'course.TheoryContent',
                '--pks', ','.join(str(theory.id) for theory in new_theory),
                '--format=json',
                '--indent=2',
                '--output', filename
            )
            export_data['exported_objects']['theory'] = {
                'count': new_theory.count(),
                'file': filename
            }
            print(f"  ✅ {new_theory.count()} nouveaux contenus théoriques exportés")
            
        if new_matching.exists():
            filename = f"new_matching_{self.timestamp}.json"
            call_command(
                'dumpdata',
                'course.MatchingExercise',
                '--pks', ','.join(str(ex.id) for ex in new_matching),
                '--format=json',
                '--indent=2',
                '--output', filename
            )
            export_data['exported_objects']['matching'] = {
                'count': new_matching.count(),
                'file': filename
            }
            print(f"  ✅ {new_matching.count()} nouveaux exercices de correspondance exportés")
            
        # Sauvegarder le manifest
        manifest_file = f"export_manifest_{self.timestamp}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        print(f"📋 Manifest sauvegardé: {manifest_file}")
        return export_data
        
    def sync_specific_app_to_production(self, app_name):
        """Synchronise une application spécifique vers la production"""
        from app_manager.models import App
        
        try:
            # Essayer d'abord par code, puis par display_name
            try:
                app = App.objects.get(code=app_name)
            except App.DoesNotExist:
                app = App.objects.get(display_name__icontains=app_name)
                
            print(f"📱 Synchronisation de l'application: {app.display_name} (code: {app.code})")
            
            # Export de l'app et ses dépendances
            filename = f"app_{app.code}_{self.timestamp}.json"
            call_command(
                'dumpdata',
                'app_manager.App',
                '--pks', str(app.id),
                '--format=json',
                '--indent=2',
                '--output', filename
            )
            
            # Déployer vers production
            self._deploy_file_to_production(filename)
            
            print(f"✅ Application {app.display_name} synchronisée vers la production")
            
        except App.DoesNotExist:
            print(f"❌ Application '{app_name}' non trouvée")
            print("📋 Applications disponibles:")
            apps = App.objects.all()
            for app in apps:
                print(f"  - {app.display_name} (code: {app.code})")
            
    def _deploy_file_to_production(self, filename):
        """Déploie un fichier vers la production"""
        env = os.environ.copy()
        env['DJANGO_ENV'] = 'production'
        
        result = subprocess.run([
            sys.executable, 'manage.py', 'loaddata', filename
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  ✅ {filename} déployé avec succès")
        else:
            print(f"  ❌ Erreur lors du déploiement de {filename}: {result.stderr}")
            
        return result.returncode == 0


def main():
    """Menu principal pour la synchronisation sélective"""
    sync = SelectiveSync()
    
    print("🔄 SYNCHRONISATION SÉLECTIVE")
    print("=" * 40)
    print()
    
    print("Options:")
    print("1. Export des changements depuis X jours")
    print("2. Synchroniser une application spécifique")
    print("3. Export des nouveautés d'aujourd'hui")
    print("4. Quitter")
    print()
    
    choice = input("Votre choix (1-4): ").strip()
    
    if choice == "1":
        days = int(input("Nombre de jours depuis lesquels chercher les changements: "))
        since_date = datetime.now() - timedelta(days=days)
        sync.export_changes_since_date(since_date)
        
    elif choice == "2":
        app_name = input("Nom de l'application à synchroniser: ").strip()
        sync.sync_specific_app_to_production(app_name)
        
    elif choice == "3":
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        sync.export_changes_since_date(today)
        
    elif choice == "4":
        print("👋 Au revoir!")
        return
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()