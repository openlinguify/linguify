#!/usr/bin/env python3
"""
Script pour installer polib et compiler les traductions sans gettext
"""

import subprocess
import sys
import os

def install_polib():
    """Installe la bibliothèque polib pour gérer les traductions"""
    print("📦 Installation de polib...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'polib'])
        print("✅ polib installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation de polib: {e}")
        return False

def compile_with_polib():
    """Compile les traductions avec polib"""
    try:
        import polib
    except ImportError:
        print("❌ polib n'est pas installé")
        return False
    
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    
    print("🔨 Compilation avec polib...")
    success_count = 0
    
    for lang_dir in os.listdir(locale_dir):
        lang_path = os.path.join(locale_dir, lang_dir)
        if not os.path.isdir(lang_path):
            continue
            
        lc_messages_path = os.path.join(lang_path, 'LC_MESSAGES')
        if not os.path.exists(lc_messages_path):
            continue
            
        po_file = os.path.join(lc_messages_path, 'django.po')
        mo_file = os.path.join(lc_messages_path, 'django.mo')
        
        if os.path.exists(po_file):
            try:
                print(f"🔄 Compilation {lang_dir}...")
                po = polib.pofile(po_file)
                po.save_as_mofile(mo_file)
                print(f"  ✅ {lang_dir}: {len(po)} entrées compilées")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {lang_dir}: Erreur - {e}")
    
    return success_count > 0

def main():
    print("🌍 Installation et compilation des traductions")
    print("=" * 50)
    
    # Étape 1: Installer polib
    if not install_polib():
        print("\n❌ Impossible d'installer polib")
        return False
    
    # Étape 2: Compiler avec polib
    print("\n🔨 Compilation des traductions...")
    if compile_with_polib():
        print("\n🎉 Compilation réussie !")
        print("\n📋 Instructions :")
        print("  1. Redémarrez le serveur Django :")
        print("     python manage.py runserver")
        print("\n  2. Testez les langues :")
        print("     http://127.0.0.1:8000/set-language/fr/")
        print("     http://127.0.0.1:8000/set-language/en/")
        print("\n✨ Le site devrait maintenant s'afficher en français !")
        return True
    else:
        print("\n❌ Échec de la compilation")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Solution alternative :")
        print("   Ajoutez temporairement à core/settings.py :")
        print("   USE_I18N = False")
        print("   LANGUAGE_CODE = 'en'")