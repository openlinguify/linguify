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
    """Corrige les séquences d'échappement invalides dans les fichiers Python."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # Option 1: Ajouter des préfixes 'r' aux chaînes qui contiennent des séquences d'échappement regex
    # Recherche des chaînes sans préfixe 'r' qui contiennent des séquences d'échappement regex
    pattern_strings = re.compile(r'(?<!r)(["\'])((?:\\d|\\w|\\s|\\b)+.*?)\\1')
    for match in pattern_strings.finditer(content):
        # Ajouter le préfixe 'r' avant la chaîne
        old_str = match.group(0)
        new_str = 'r' + old_str
        content = content.replace(old_str, new_str)
        modified = True

    # Option 2: Remplacer directement les séquences d'échappement problématiques
    if '\\d' in content:
        # Remplacer \d par [0-9]
        content = re.sub(r'(?<!r)(["\']).*?\\d', lambda m: m.group(0).replace('\\d', '[0-9]'), content)
        modified = True

    # Autres corrections d'échappement courantes
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return modified


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