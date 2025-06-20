#!/bin/bash

# Script d'installation et configuration PostgreSQL pour Linguify
# Ce script configure PostgreSQL pour le développement local

echo "🚀 Configuration PostgreSQL pour Linguify"
echo "==========================================="

# Vérifier si PostgreSQL est installé
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL n'est pas installé."
    echo ""
    echo "📥 Instructions d'installation PostgreSQL sur WSL2/Ubuntu:"
    echo "-----------------------------------------------------------"
    echo "1. Mettre à jour les paquets:"
    echo "   sudo apt update"
    echo ""
    echo "2. Installer PostgreSQL:"
    echo "   sudo apt install postgresql postgresql-contrib"
    echo ""
    echo "3. Démarrer le service:"
    echo "   sudo service postgresql start"
    echo ""
    echo "4. Configurer le mot de passe pour l'utilisateur postgres:"
    echo "   sudo -u postgres psql"
    echo "   \\password postgres"
    echo "   (Entrez le mot de passe: azerty)"
    echo "   \\q"
    echo ""
    echo "5. Relancer ce script:"
    echo "   bash setup_postgresql.sh"
    echo ""
    exit 1
fi

echo "✅ PostgreSQL est installé!"

# Vérifier si le service est démarré
if ! sudo service postgresql status | grep -q "online"; then
    echo "🔄 Démarrage du service PostgreSQL..."
    sudo service postgresql start
    sleep 2
fi

echo "✅ Service PostgreSQL démarré!"

# Configuration des bases de données
echo ""
echo "🗄️  Configuration des bases de données..."
echo "----------------------------------------"

# Base de données de développement
echo "📊 Création de la base de développement..."
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = 'db_linguify_dev';" | grep -q 1 || {
    echo "   Création de db_linguify_dev..."
    sudo -u postgres createdb db_linguify_dev
    echo "   ✅ Base db_linguify_dev créée!"
}

# Base de données de production locale (optionnelle)
echo "📊 Création de la base de production locale..."
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = 'db_linguify_prod';" | grep -q 1 || {
    echo "   Création de db_linguify_prod..."
    sudo -u postgres createdb db_linguify_prod
    echo "   ✅ Base db_linguify_prod créée!"
}

# Vérifier la configuration utilisateur
echo ""
echo "👤 Vérification de l'utilisateur postgres..."
if sudo -u postgres psql -c "\\du" | grep -q "postgres.*Superuser"; then
    echo "   ✅ Utilisateur postgres configuré!"
else
    echo "   ⚠️  Configurez le mot de passe postgres:"
    echo "   sudo -u postgres psql"
    echo "   \\password postgres"
    echo "   (Entrez: azerty)"
fi

echo ""
echo "🎯 Configuration terminée!"
echo "========================="
echo ""
echo "📝 Étapes suivantes:"
echo "1. Vérifiez que DJANGO_ENV=\"development\" dans votre .env"
echo "2. Lancez les migrations:"
echo "   python manage.py migrate"
echo "3. Pour accéder aux CVs de production:"
echo "   python manage.py prod_shell"
echo ""
echo "🔗 Connexions configurées:"
echo "• Développement: localhost:5432/db_linguify_dev"
echo "• Production: Supabase (via DJANGO_ENV=\"production\")"
echo ""
echo "✨ Installation terminée!"