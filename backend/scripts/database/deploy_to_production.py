#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de déploiement sélectif vers la production Supabase
Permet de pousser des données spécifiques (apps, cours, etc.) depuis le développement vers la production
"""

import os
import sys
import django
import json
from datetime import datetime
import subprocess

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.core import serializers
from django.apps import apps


class ProductionDeployer:
    """Gestionnaire de déploiement vers la production"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_dir = f"deploy_temp_{self.timestamp}"
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def export_apps(self, app_ids=None):
        """Exporte les applications spécifiques"""
        print("📱 Export des applications...")
        
        models_to_export = [
            'app_manager.App',
            'app_manager.AppDataRetention',
        ]
        
        if app_ids:
            # Export sélectif par IDs
            for model_name in models_to_export:
                filename = f"{self.temp_dir}/apps_{model_name.split('.')[1].lower()}.json"
                call_command(
                    'dumpdata', 
                    model_name,
                    '--pks', ','.join(map(str, app_ids)),
                    '--format=json',
                    '--indent=2',
                    '--output', filename
                )
                print(f"  ✅ {model_name} exporté vers {filename}")
        else:
            # Export complet des apps
            filename = f"{self.temp_dir}/all_apps.json"
            call_command(
                'dumpdata',
                *models_to_export,
                '--format=json',
                '--indent=2',
                '--output', filename
            )
            print(f"  ✅ Toutes les apps exportées vers {filename}")
            
    def export_courses(self, course_ids=None, unit_ids=None):
        """Exporte les cours spécifiques"""
        print("📚 Export des cours...")
        
        models_to_export = [
            'course.Course',
            'course.Unit', 
            'course.Lesson',
            'course.ContentLesson',
            'course.VocabularyList',
            'course.Numbers',
            'course.TheoryContent',
            'course.MultipleChoiceQuestion',
            'course.MatchingExercise',
            'course.SpeakingExercise',
            'course.TestRecap',
            'course.TestRecapQuestion',
            'course.TestRecapResult',
        ]
        
        if course_ids:
            for model_name in models_to_export:
                filename = f"{self.temp_dir}/courses_{model_name.split('.')[1].lower()}.json"
                try:
                    call_command(
                        'dumpdata',
                        model_name,
                        '--format=json',
                        '--indent=2',
                        '--output', filename
                    )
                    print(f"  ✅ {model_name} exporté")
                except Exception as e:
                    print(f"  ⚠️ Erreur {model_name}: {e}")
        else:
            filename = f"{self.temp_dir}/all_courses.json"
            call_command(
                'dumpdata',
                *models_to_export,
                '--format=json',
                '--indent=2',
                '--output', filename
            )
            print(f"  ✅ Tous les cours exportés vers {filename}")
            
    def export_custom_selection(self, models_and_filters):
        """
        Export personnalisé avec filtres
        models_and_filters = {
            'app_manager.App': {'name__icontains': 'nouvelle_app'},
            'course.Course': {'title__icontains': 'nouveau_cours'}
        }
        """
        print("🎯 Export personnalisé...")
        
        for model_name, filters in models_and_filters.items():
            try:
                app_label, model_class_name = model_name.split('.')
                model_class = apps.get_model(app_label, model_class_name)
                
                # Filtrer les objets
                objects = model_class.objects.filter(**filters)
                
                if objects.exists():
                    filename = f"{self.temp_dir}/custom_{model_class_name.lower()}.json"
                    
                    # Serialiser manuellement pour plus de contrôle
                    data = serializers.serialize('json', objects, indent=2)
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(data)
                        
                    print(f"  ✅ {model_name}: {objects.count()} objets exportés")
                else:
                    print(f"  ⚠️ {model_name}: Aucun objet trouvé avec les filtres {filters}")
                    
            except Exception as e:
                print(f"  ❌ Erreur {model_name}: {e}")
                
    def deploy_to_production(self):
        """Déploie les fichiers exportés vers la production"""
        print("🚀 Déploiement vers la production...")
        
        # Changer l'environnement vers production
        env = os.environ.copy()
        env['DJANGO_ENV'] = 'production'
        
        # Trouver tous les fichiers JSON à déployer
        json_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.json')]
        
        if not json_files:
            print("  ⚠️ Aucun fichier à déployer trouvé")
            return False
            
        print(f"  📁 Fichiers à déployer: {', '.join(json_files)}")
        
        # Confirmation de sécurité
        response = input("  ⚠️ ATTENTION: Déploiement vers PRODUCTION. Continuer? (oui/non): ")
        if response.lower() not in ['oui', 'yes', 'y']:
            print("  ❌ Déploiement annulé")
            return False
            
        # Déployer chaque fichier
        success_count = 0
        for json_file in json_files:
            filepath = os.path.join(self.temp_dir, json_file)
            
            try:
                print(f"  📤 Déploiement de {json_file}...")
                
                result = subprocess.run([
                    sys.executable, 'manage.py', 'loaddata', filepath
                ], env=env, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(self.temp_dir)))
                
                if result.returncode == 0:
                    print(f"    ✅ {json_file} déployé avec succès")
                    success_count += 1
                else:
                    print(f"    ❌ Erreur {json_file}: {result.stderr}")
                    
            except Exception as e:
                print(f"    ❌ Exception {json_file}: {e}")
                
        print(f"  📊 Résultat: {success_count}/{len(json_files)} fichiers déployés")
        return success_count == len(json_files)
        
    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Fichiers temporaires supprimés: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")


def main():
    """Menu principal interactif"""
    deployer = ProductionDeployer()
    
    try:
        print("🚀 DÉPLOIEMENT VERS PRODUCTION SUPABASE")
        print("=" * 50)
        print()
        
        print("Options de déploiement:")
        print("1. Déployer nouvelles applications")
        print("2. Déployer nouveaux cours")
        print("3. Déploiement personnalisé")
        print("4. Quitter")
        print()
        
        choice = input("Votre choix (1-4): ").strip()
        
        if choice == "1":
            # Déploiement d'applications
            print("\n📱 DÉPLOIEMENT D'APPLICATIONS")
            print("Voulez-vous déployer:")
            print("a. Toutes les nouvelles applications")
            print("b. Applications spécifiques par ID")
            
            sub_choice = input("Votre choix (a/b): ").strip().lower()
            
            if sub_choice == "a":
                deployer.export_apps()
            elif sub_choice == "b":
                ids_input = input("IDs des applications (séparés par des virgules): ")
                app_ids = [int(id.strip()) for id in ids_input.split(',') if id.strip().isdigit()]
                deployer.export_apps(app_ids)
                
        elif choice == "2":
            # Déploiement de cours
            print("\n📚 DÉPLOIEMENT DE COURS")
            deployer.export_courses()
            
        elif choice == "3":
            # Déploiement personnalisé
            print("\n🎯 DÉPLOIEMENT PERSONNALISÉ")
            print("Exemple: déployer une app avec un nom spécifique")
            
            app_name = input("Nom de l'application à déployer (ou ENTER pour passer): ").strip()
            course_name = input("Nom du cours à déployer (ou ENTER pour passer): ").strip()
            
            filters = {}
            if app_name:
                filters['app_manager.App'] = {'name__icontains': app_name}
            if course_name:
                filters['course.Course'] = {'title__icontains': course_name}
                
            if filters:
                deployer.export_custom_selection(filters)
            else:
                print("Aucun filtre spécifié")
                return
                
        elif choice == "4":
            print("👋 Au revoir!")
            return
        else:
            print("❌ Choix invalide")
            return
            
        # Procéder au déploiement
        if deployer.deploy_to_production():
            print("\n🎉 Déploiement terminé avec succès!")
        else:
            print("\n⚠️ Déploiement partiellement réussi ou échoué")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Déploiement interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
    finally:
        deployer.cleanup()


if __name__ == "__main__":
    main()