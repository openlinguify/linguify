#!/bin/bash

echo "🔧 Installation de toutes les dépendances pour les 3 projets Linguify..."

# Backend (avec Poetry)
echo "📦 Backend - Installation avec Poetry..."
cd backend
poetry add Pillow
poetry add whitenoise
poetry add dj-database-url
cd ..

# Portal (avec pip)
echo "📦 Portal - Installation avec pip..."
./portal/venv/bin/pip install -r portal/requirements.txt

# LMS (avec pip)
echo "📦 LMS - Installation avec pip..."
./lms/venv/bin/pip install -r lms/requirements.txt

echo "✅ Installation terminée!"