"""
Export des données de production depuis Supabase
Usage: DJANGO_ENV="production" puis lancer ce script
"""
import os
import sys
import json

# Forcer UTF-8
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from django.core import serializers
from django.apps import apps
from django.db import connection

print("📥 Export des données de production depuis Supabase")
print("=" * 60)

# Vérifier qu'on est bien en production
print(f"🔗 Connecté à: {connection.settings_dict['HOST']}")

if 'supabase' not in connection.settings_dict['HOST']:
    print("❌ ERREUR: Pas connecté à Supabase!")
    print("   Changez DJANGO_ENV='production' dans .env")
    sys.exit(1)

# Apps à exporter (dans l'ordre pour éviter les contraintes)
APPS_TO_EXPORT = [
    'authentication',
    'app_manager', 
    'course',
    'jobs',
    'notebook',
    'revision',
]

try:
    all_data = []
    total_objects = 0
    
    print("\n📊 Export par application:")
    
    for app_name in APPS_TO_EXPORT:
        try:
            app_config = apps.get_app_config(app_name)
            models = app_config.get_models()
            
            print(f"\n📱 App: {app_name}")
            
            for model in models:
                try:
                    objects = model.objects.all()
                    count = objects.count()
                    
                    if count > 0:
                        print(f"   {model.__name__}: {count} objets")
                        
                        # Sérialiser sans clés naturelles pour éviter les problèmes
                        serialized = serializers.serialize('json', objects)
                        model_data = json.loads(serialized)
                        all_data.extend(model_data)
                        total_objects += count
                        
                except Exception as e:
                    print(f"   ⚠️  {model.__name__}: {e}")
            
        except Exception as e:
            print(f"❌ App {app_name}: {e}")
    
    # Sauvegarder
    output_file = 'production_export.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    size_mb = os.path.getsize(output_file) / 1024 / 1024
    
    print(f"\n✅ Export terminé avec succès!")
    print(f"📁 Fichier: {output_file}")
    print(f"📊 Taille: {size_mb:.2f} MB")
    print(f"🎯 Total objets: {total_objects}")
    
    print(f"\n🎯 Prochaines étapes:")
    print(f"1. Changez DJANGO_ENV='development' dans .env")
    print(f"2. python scripts/database/import_to_development.py")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()