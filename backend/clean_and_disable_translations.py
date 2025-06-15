#!/usr/bin/env python3
"""
Solution d'urgence : Nettoie les traductions corrompues et configure le site pour fonctionner
"""

import os
import shutil

def clean_mo_files():
    """Supprime tous les fichiers .mo corrompus"""
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    
    print("🧹 Nettoyage des fichiers .mo corrompus...")
    
    deleted_count = 0
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.mo'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"  🗑️ Supprimé: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ⚠️ Erreur lors de la suppression de {file_path}: {e}")
    
    print(f"✅ {deleted_count} fichiers .mo supprimés")

def create_temporary_settings():
    """Crée un fichier de configuration temporaire pour désactiver les traductions si nécessaire"""
    settings_override = """
# Ajoutez ceci temporairement à settings.py si les traductions posent problème :
USE_I18N = False
USE_L10N = False
LANGUAGE_CODE = 'en'
"""
    
    temp_file = os.path.join(os.path.dirname(__file__), 'settings_override_temp.txt')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(settings_override)
    
    print(f"📝 Configuration de secours créée dans: {temp_file}")

def update_language_settings():
    """Met à jour les paramètres de langue pour une configuration stable"""
    settings_file = os.path.join(os.path.dirname(__file__), 'core', 'settings.py')
    
    try:
        # Lire le fichier settings.py
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si les paramètres multilingues sont corrects
        if "USE_I18N = True" in content and "LANGUAGE_CODE = 'en'" in content:
            print("✅ Paramètres de langue corrects dans settings.py")
            return True
        else:
            print("⚠️ Paramètres de langue à vérifier dans settings.py")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de settings.py: {e}")
        return False

def main():
    print("🔧 Script de nettoyage et réparation des traductions")
    print("=" * 55)
    
    # Étape 1: Nettoyer les fichiers .mo corrompus
    clean_mo_files()
    
    # Étape 2: Vérifier les paramètres
    print("\n🔍 Vérification des paramètres...")
    update_language_settings()
    
    # Étape 3: Créer un fichier de secours
    print("\n📋 Création des fichiers de secours...")
    create_temporary_settings()
    
    # Instructions
    print("\n🎯 Instructions :")
    print("  1. Essayez de redémarrer Django maintenant :")
    print("     python manage.py runserver")
    print("")
    print("  2. Si l'erreur persiste, utilisez une des solutions :")
    print("")
    print("     Solution A - Site en anglais uniquement :")
    print("     Ajoutez temporairement à core/settings.py :")
    print("     USE_I18N = False")
    print("     LANGUAGE_CODE = 'en'")
    print("")
    print("     Solution B - Installer gettext sur Windows :")
    print("     1. Installez Git for Windows (inclut gettext)")
    print("     2. Redémarrez le terminal")
    print("     3. Exécutez: python manage.py compilemessages")
    print("")
    print("  3. Testez le site :")
    print("     http://127.0.0.1:8000/")
    print("")
    print("✨ Le site devrait maintenant fonctionner !")

if __name__ == "__main__":
    main()