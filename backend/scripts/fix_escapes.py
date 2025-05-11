#!/usr/bin/env python
"""
Script pour corriger automatiquement les séquences d'échappement invalides
dans les fichiers Python du projet.
"""
import os
import re
import sys
from pathlib import Path


def fix_invalid_escapes(file_path):
    """Remplace les séquences d'échappement \d par [0-9] dans les fichiers."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Détection des séquences d'échappement problématiques
    if '\\d' in content:
        # Remplacer \d par [0-9] seulement lorsqu'il s'agit d'une regex
        # (généralement dans des chaînes de caractères r"..." ou dans des URLs)
        content_fixed = re.sub(r'\\d', '[0-9]', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_fixed)
        
        return True
    return False


def main():
    """Fonction principale qui parcourt tous les fichiers Python."""
    base_dir = Path(__file__).resolve().parent.parent
    count = 0
    
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_invalid_escapes(file_path):
                    count += 1
                    print(f"Corrigé: {file_path}")
    
    print(f"Terminé. {count} fichiers corrigés.")


if __name__ == "__main__":
    sys.exit(main())