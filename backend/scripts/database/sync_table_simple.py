#!/usr/bin/env python3
"""
Script simplifié de synchronisation granulaire des tables
Utilise directement les commandes shell pour éviter les problèmes de rechargement Django
"""

import os
import sys
import subprocess
import tempfile

def sync_table_to_production(app_name, table_name, target_env):
    """Synchronise une table spécifique vers la production"""
    
    print(f"🔄 Synchronisation de {app_name}.{table_name} vers {target_env}")
    
    backend_dir = '/mnt/c/Users/louis/WebstormProjects/linguify/backend'
    os.chdir(backend_dir)
    
    # Configuration des environnements
    if target_env.lower() in ['prod', 'production']:
        target_env_name = 'production'
        print("🚀 Cible: Production (Supabase)")
    else:
        target_env_name = 'development'
        print("🏗️  Cible: Développement (PostgreSQL local)")
    
    # Convertir le nom de table en nom de modèle Django
    model_name = table_name.title()  # category -> Category
    
    try:
        # 1. Export depuis développement
        print("📤 Export des données depuis développement...")
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False)
        temp_file_path = temp_file.name
        temp_file.close()
        
        export_cmd = [
            'poetry', 'run', 'python', 'manage.py', 'dumpdata',
            f'{app_name}.{model_name}',
            '--format=json',
            '--indent=2'
        ]
        
        # Export en développement
        export_env = os.environ.copy()
        export_env['DJANGO_ENV'] = 'development'
        
        result = subprocess.run(
            export_cmd,
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=export_env
        )
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'export: {result.stderr}")
            os.unlink(temp_file_path)
            return False
        
        export_data = result.stdout.strip()
        
        # Nettoyer les lignes parasites des messages de connexion
        lines = export_data.split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            if line.strip().startswith('[') or line.strip().startswith('{'):
                in_json = True
            if in_json:
                json_lines.append(line)
        
        export_data = '\n'.join(json_lines)
        print(f"📦 Données exportées: {len(export_data)} caractères")
        
        if not export_data or export_data == "[]":
            print("⚠️  Aucune donnée à synchroniser")
            os.unlink(temp_file_path)
            return True
        
        # Sauvegarder les données
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            f.write(export_data)
        
        print(f"💾 Données sauvegardées dans {temp_file_path}")
        
        # 2. Nettoyer les données existantes (optionnel)
        print(f"🧹 Nettoyage des données existantes...")
        
        # Déterminer le chemin d'import correct
        if app_name == 'blog':
            import_path = 'core.blog'
        elif app_name in ['course', 'notebook', 'revision', 'quizz', 'chat', 'community']:
            import_path = f'apps.{app_name}'
        else:
            import_path = app_name
            
        clear_cmd = [
            'poetry', 'run', 'python', 'manage.py', 'shell', '-c',
            f"from {import_path}.models import {model_name}; {model_name}.objects.all().delete(); print('Données supprimées')"
        ]
        
        # Import dans l'environnement cible
        import_env = os.environ.copy()
        import_env['DJANGO_ENV'] = target_env_name
        
        clear_result = subprocess.run(
            clear_cmd,
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=import_env
        )
        
        if clear_result.returncode == 0:
            print(f"✅ {clear_result.stdout.strip()}")
        
        # 3. Import vers la cible
        print(f"📥 Import vers {target_env_name}...")
        
        import_cmd = [
            'poetry', 'run', 'python', 'manage.py', 'loaddata',
            temp_file_path
        ]
        
        result = subprocess.run(
            import_cmd,
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=import_env
        )
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de l'import: {result.stderr}")
            # Nettoyer le fichier temporaire
            os.unlink(temp_file_path)
            return False
        
        print("✅ Import réussi")
        
        # Vérifier les données dans l'environnement cible
        print("📊 Vérification des données...")
        count_cmd = [
            'poetry', 'run', 'python', 'manage.py', 'shell', '-c',
            f"from {import_path}.models import {model_name}; print(f'Lignes: {{{model_name}.objects.count()}}')"
        ]
        
        result = subprocess.run(
            count_cmd,
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=import_env
        )
        
        if result.returncode == 0:
            print(f"📈 {result.stdout.strip()}")
        
        # Nettoyer le fichier temporaire
        os.unlink(temp_file_path)
        
        print(f"✅ Synchronisation terminée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        return False

def main():
    if len(sys.argv) != 4:
        print("❌ Usage: python sync_table_simple.py <app> <table> <target>")
        print("📝 Exemples:")
        print("  python sync_table_simple.py blog category prod")
        print("  python sync_table_simple.py course lesson prod")
        print("  python sync_table_simple.py blog tag prod")
        sys.exit(1)
    
    app_name = sys.argv[1]
    table_name = sys.argv[2]
    target_env = sys.argv[3]
    
    print(f"🎯 Synchronisation {app_name}.{table_name} → {target_env}")
    
    success = sync_table_to_production(app_name, table_name, target_env)
    
    if success:
        print("✅ Synchronisation réussie")
        sys.exit(0)
    else:
        print("❌ Synchronisation échouée")
        sys.exit(1)

if __name__ == "__main__":
    main()