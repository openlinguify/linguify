#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de synchronisation rapide d'une application spécifique
Usage: python quick_sync_app.py nom_de_app
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from scripts.database.selective_sync import SelectiveSync


def main():
    if len(sys.argv) != 2:
        print("❌ Usage: python quick_sync_app.py <nom_de_app>")
        print("📝 Exemple: python quick_sync_app.py mon_super_quiz")
        sys.exit(1)
        
    app_name = sys.argv[1]
    
    print(f"🚀 Synchronisation rapide de l'application: {app_name}")
    print("=" * 50)
    
    sync = SelectiveSync()
    sync.sync_specific_app_to_production(app_name)
    
    print("✅ Terminé!")


if __name__ == "__main__":
    main()