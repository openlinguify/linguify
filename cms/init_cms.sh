#!/bin/bash

# Script d'initialisation du CMS Linguify
echo "🚀 Initialisation du CMS Linguify..."

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "✅ Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -r requirements.txt

# Créer la base de données PostgreSQL si nécessaire
echo "🗄️ Configuration de la base de données..."
createdb linguify_cms 2>/dev/null || echo "Base de données déjà existante"

# Faire les migrations
echo "🔄 Application des migrations..."
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
echo "👤 Création du superutilisateur..."
python manage.py createsuperuser --noinput --username admin --email admin@linguify.com || echo "Superutilisateur déjà existant"

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ CMS Linguify initialisé avec succès!"
echo "🌐 Démarrez le serveur avec: make cms"
echo "🔑 Connectez-vous sur http://127.0.0.1:8002/admin avec admin/admin"