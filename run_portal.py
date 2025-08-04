#!/usr/bin/env python
"""
Script pour lancer le portal depuis la racine
"""
import os
import sys
import subprocess

# Aller dans le dossier portal et lancer le serveur
portal_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portal')
os.chdir(portal_dir)

# Lancer le serveur
subprocess.run([sys.executable, 'manage.py', 'runserver', '8080'])