#!/bin/bash

# Script de démarrage du CMS Linguify
echo "🚀 Démarrage du CMS Linguify..."

# Naviguer vers le répertoire du CMS
cd "$(dirname "$0")"

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier les migrations
echo "🔄 Vérification des migrations..."
python manage.py makemigrations
python manage.py migrate

# Collecter les fichiers statiques
echo "📦 Collection des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# Afficher les informations d'accès
echo ""
echo "=" * 60
echo "📋 CMS LINGUIFY - INFORMATIONS D'ACCÈS"
echo "=" * 60
echo "🌐 URL Admin: http://localhost:8081/admin/"
echo "👨‍🏫 URL Teachers: http://localhost:8081/teachers/"
echo ""
echo "🔑 COMPTES DE TEST:"
echo "   Admin (Superuser):"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
echo "   Professeur 1:"
echo "     Username: prof1"
echo "     Password: prof123"
echo ""
echo "   Professeur 2:"
echo "     Username: prof2"  
echo "     Password: prof123"
echo ""
echo "=" * 60
echo "💡 COMMANDES UTILES:"
echo "   • Créer un superuser: python create_superuser.py [username] [email] [password]"
echo "   • Arrêter le serveur: Ctrl+C"
echo "   • Créer des migrations: python manage.py makemigrations [app_name]"
echo "=" * 60

# Démarrer le serveur de développement
echo ""
echo "🚀 Démarrage du serveur Django..."
echo "   Le CMS sera accessible sur: http://localhost:8081/"
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

python manage.py runserver