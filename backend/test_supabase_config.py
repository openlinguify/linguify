#!/usr/bin/env python3
"""
Test simple de configuration Supabase
"""
import os
from pathlib import Path

# Chargement du .env
BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / '.env'

print(f"Lecture du fichier .env: {env_file}")
print(f"Fichier existe: {env_file.exists()}")

if env_file.exists():
    with open(env_file, 'r') as f:
        content = f.read()
        print(f"Contenu du fichier .env (premiers 500 caractères):")
        print(content[:500])
        
        # Chercher les variables Supabase
        lines = content.split('\n')
        supabase_vars = [line for line in lines if 'SUPABASE' in line and '=' in line]
        print(f"\nVariables Supabase trouvées:")
        for var in supabase_vars:
            if 'JWT_SECRET' in var:
                # Masquer le secret pour la sécurité
                key, value = var.split('=', 1)
                print(f"{key}={value[:20]}... (longueur: {len(value)})")
            else:
                print(var)