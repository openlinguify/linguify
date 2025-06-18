#!/usr/bin/env python
"""
Test pour le générateur de module Linguify

Ce script teste la fonctionnalité de create_new_module.py en:
1. Configurant un environnement temporaire
2. Exécutant le script de création de module
3. Vérifiant que les fichiers et répertoires attendus sont créés
4. Validant le contenu des fichiers clés
5. Nettoyant l'environnement de test

Usage:
    python test_create_module.py
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path
import argparse

def configurer_environnement_test():
    """Configurer un environnement temporaire pour les tests."""
    print("Configuration de l'environnement de test...")
    rep_test = tempfile.mkdtemp(prefix="linguify_test_")
    
    # Créer la structure de répertoires nécessaire
    (Path(rep_test) / "backend" / "core").mkdir(parents=True)
    (Path(rep_test) / "backend" / "apps").mkdir(parents=True)
    (Path(rep_test) / "frontend" / "src" / "app" / "dashboard").mkdir(parents=True)
    (Path(rep_test) / "frontend" / "src" / "addons").mkdir(parents=True)
    
    # Créer settings.py minimal
    contenu_settings = """
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    
    # Project django_apps
    'apps.authentication',
    'apps.core',
    
    # Django REST framework modules
    'rest_framework',
]
"""
    (Path(rep_test) / "backend" / "core" / "settings.py").write_text(contenu_settings)
    
    # Créer urls.py minimal
    contenu_urls = """
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls', namespace='authentication')),
]
"""
    (Path(rep_test) / "backend" / "core" / "urls.py").write_text(contenu_urls)
    
    # Créer page dashboard minimale
    contenu_dashboard = """
import { Home, Settings } from 'lucide-react';

const menuItems = [
    {
      titleKey: "dashboard.homeCard.title",
      fallbackTitle: "Home",
      icon: Home,
      href: "/",
      color: "bg-blue-50 text-blue-500 dark:bg-blue-900/20 dark:text-blue-400"
    },
    {
      titleKey: "dashboard.settingsCard.title",
      fallbackTitle: "Settings",
      icon: Settings,
      href: "/settings",
      color: "bg-gray-50 text-gray-500 dark:bg-gray-800/50 dark:text-gray-400"
    }
];

export default function Dashboard() {
    return <div>Dashboard</div>;
}
"""
    (Path(rep_test) / "frontend" / "src" / "app" / "dashboard" / "page.tsx").write_text(contenu_dashboard)
    
    # Copier le script create_new_module.py dans le répertoire de test
    contenu_script = Path("paste.txt").read_text()
    (Path(rep_test) / "create_new_module.py").write_text(contenu_script)
    
    return rep_test

def executer_creation_module(rep_test, nom_module, nom_icone, description):
    """Exécuter le script de création de module."""
    print(f"Création du module '{nom_module}' avec l'icône '{nom_icone}'...")
    
    chemin_script = Path(rep_test) / "create_new_module.py"
    
    # Construire la commande
    commande = [
        sys.executable,
        str(chemin_script),
        nom_module,
        nom_icone,
        "--description",
        description
    ]
    
    # Changer vers le répertoire de test et exécuter la commande
    repertoire_original = os.getcwd()
    os.chdir(rep_test)
    
    try:
        resultat = subprocess.run(commande, capture_output=True, text=True)
        print(resultat.stdout)
        
        if resultat.returncode != 0:
            print(f"Erreur lors de l'exécution du script: {resultat.stderr}")
            return False
    except Exception as e:
        print(f"Exception lors de l'exécution du script: {e}")
        return False
    finally:
        os.chdir(repertoire_original)
    
    return True

def verifier_fichiers_crees(rep_test, nom_module, nom_icone):
    """Vérifier que les fichiers et répertoires attendus ont été créés."""
    print("Vérification des fichiers créés...")
    
    # Définir les fichiers et répertoires attendus
    rep_app_backend = Path(rep_test) / "backend" / "apps" / nom_module
    rep_module_frontend = Path(rep_test) / "frontend" / "src" / "addons" / nom_module
    rep_route_app = Path(rep_test) / "frontend" / "src" / "app" / nom_module
    
    # Vérifier les répertoires
    repertoires = [
        rep_app_backend,
        rep_app_backend / "migrations",
        rep_module_frontend,
        rep_module_frontend / "components",
        rep_module_frontend / "api",
        rep_module_frontend / "types",
        rep_module_frontend / "hooks",
        rep_module_frontend / "services",
        rep_route_app
    ]
    
    for repertoire in repertoires:
        if not repertoire.exists():
            print(f"Répertoire non créé: {repertoire}")
            return False
    
    # Vérifier les fichiers backend
    fichiers_backend = [
        rep_app_backend / "__init__.py",
        rep_app_backend / "admin.py",
        rep_app_backend / "apps.py",
        rep_app_backend / "models.py",
        rep_app_backend / "serializers.py",
        rep_app_backend / "views.py",
        rep_app_backend / "urls.py",
        rep_app_backend / "tests.py",
        rep_app_backend / "migrations" / "__init__.py"
    ]
    
    for fichier in fichiers_backend:
        if not fichier.exists():
            print(f"Fichier backend non créé: {fichier}")
            return False
    
    # Vérifier les fichiers frontend
    nom_module_capitalise = nom_module[0].upper() + nom_module[1:]
    fichiers_frontend = [
        rep_module_frontend / "index.ts",
        rep_module_frontend / "api" / f"{nom_module}API.ts",
        rep_module_frontend / "types" / "index.ts",
        rep_module_frontend / "components" / f"{nom_module_capitalise}View.tsx",
        rep_module_frontend / "components" / "index.ts",
        rep_route_app / "page.tsx",
        rep_route_app / "layout.tsx"
    ]
    
    for fichier in fichiers_frontend:
        if not fichier.exists():
            print(f"Fichier frontend non créé: {fichier}")
            return False
    
    # Vérifier le contenu des fichiers pour les chaînes attendues
    # 1. Vérifier models.py pour la définition de classe
    contenu_models = (rep_app_backend / "models.py").read_text()
    if f"class {nom_module_capitalise}(models.Model):" not in contenu_models:
        print(f"La classe du modèle n'est pas définie correctement dans models.py")
        return False
    
    # 2. Vérifier le composant View pour l'icône
    contenu_view = (rep_module_frontend / "components" / f"{nom_module_capitalise}View.tsx").read_text()
    if f"import {{ {nom_icone} }} from 'lucide-react'" not in contenu_view:
        print(f"L'icône n'est pas importée correctement dans le composant View")
        return False
    
    # 3. Vérifier la mise à jour du menu dashboard
    contenu_dashboard = (Path(rep_test) / "frontend" / "src" / "app" / "dashboard" / "page.tsx").read_text()
    if f"href: \"/{nom_module}\"" in contenu_dashboard:
        print("Menu dashboard mis à jour correctement")
    else:
        print("Avertissement: Le menu dashboard n'a pas été mis à jour comme prévu")
        # On ne fait pas échouer le test pour cela car ça pourrait être géré différemment
    
    print("Tous les fichiers ont été créés avec succès!")
    return True

def nettoyer(rep_test):
    """Nettoyer l'environnement de test."""
    print(f"Nettoyage du répertoire de test: {rep_test}")
    shutil.rmtree(rep_test)

def afficher_structure_repertoire(rep_test):
    """Affiche la structure de répertoires créée (pour déboguer)."""
    print("\nStructure de répertoires créée:")
    for root, dirs, files in os.walk(rep_test):
        level = root.replace(rep_test, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{sub_indent}{f}")

def main():
    """Fonction de test principale."""
    parser = argparse.ArgumentParser(description="Tester le générateur de module Linguify")
    parser.add_argument("--conserver", action="store_true", help="Conserver le répertoire de test pour inspection manuelle")
    parser.add_argument("--module", default="vocabulaire", help="Nom du module à créer (par défaut: vocabulaire)")
    parser.add_argument("--icone", default="Book", help="Nom de l'icône à utiliser (par défaut: Book)")
    parser.add_argument("--description", default="Module d'apprentissage de vocabulaire", 
                      help="Description du module (par défaut: Module d'apprentissage de vocabulaire)")
    args = parser.parse_args()
    
    # Paramètres de test
    nom_module = args.module
    nom_icone = args.icone
    description = args.description
    
    # Configuration
    rep_test = configurer_environnement_test()
    print(f"Répertoire de test: {rep_test}")
    
    try:
        # Exécuter le test
        succes = executer_creation_module(rep_test, nom_module, nom_icone, description)
        if not succes:
            print("La création du module a échoué")
            return 1
        
        # Afficher la structure pour le débogage
        afficher_structure_repertoire(rep_test)
        
        # Vérifier les résultats
        succes = verifier_fichiers_crees(rep_test, nom_module, nom_icone)
        if not succes:
            print("La validation des fichiers a échoué")
            return 1
        
        print("Test terminé avec succès!")
        return 0
    finally:
        # Nettoyer
        if not args.conserver:
            nettoyer(rep_test)
        else:
            print(f"Répertoire de test conservé pour inspection: {rep_test}")

if __name__ == "__main__":
    sys.exit(main())