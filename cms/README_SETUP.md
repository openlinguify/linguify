# 📚 CMS Linguify - Guide de Configuration

## 🚀 Démarrage Rapide

### 1. Démarrer le CMS
```bash
./start_cms.sh
```

### 2. Accès aux Interfaces

#### Interface Admin Django
- **URL**: http://localhost:8000/admin/
- **Compte Admin**:
  - Username: `admin`
  - Password: `admin123`

#### Interface Professeurs
- **URL**: http://localhost:8000/teachers/
- **Comptes Professeurs**:
  - **Marie Dupont**: `prof1` / `prof123`
  - **Jean Martin**: `prof2` / `prof123`

## 👥 Comptes Utilisateurs

### Superuser (Admin)
- **Username**: admin
- **Email**: admin@linguify.com
- **Password**: admin123
- **Accès**: Admin Django + Interface Professeur
- **Statut**: Approuvé, Taux: €50/h

### Professeurs de Test
1. **Marie Dupont**
   - **Username**: prof1
   - **Email**: prof1@linguify.com
   - **Password**: prof123
   - **Statut**: Approuvé, Taux: €30/h

2. **Jean Martin**
   - **Username**: prof2
   - **Email**: prof2@linguify.com
   - **Password**: prof123
   - **Statut**: Approuvé, Taux: €30/h

## 🛠️ Commandes Utiles

### Créer un Superuser
```bash
# Superuser par défaut
python create_superuser.py

# Superuser personnalisé
python create_superuser.py [username] [email] [password]
```

### Créer un Professeur
```python
# Dans le shell Python
from create_superuser import create_teacher_user
create_teacher_user('username', 'email@example.com', 'password', 'Prénom', 'Nom')
```

### Gestion Django
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Créer des migrations
python manage.py makemigrations [app_name]

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic

# Shell Django
python manage.py shell

# Démarrer le serveur
python manage.py runserver
```

## 📁 Structure des Applications

### `/teachers/` - Gestion des Professeurs
- **Dashboard**: Vue d'ensemble avec statistiques
- **Profil**: Gestion du profil multilingue
- **Cours**: Liste et gestion des cours réservés
- **Disponibilités**: Définition des créneaux horaires
- **Annonces**: Création de promotions et annonces

### `/admin/` - Interface Admin
- Gestion complète de tous les modèles
- Utilisateurs et permissions
- Configuration du système

## 🎯 Fonctionnalités Disponibles

### Dashboard Professeur
- ✅ Statistiques en temps réel
- ✅ Prochains cours
- ✅ Actions rapides
- ✅ Statut du profil

### Gestion des Cours
- ✅ Liste paginée avec filtres
- ✅ Statuts détaillés (programmé, confirmé, terminé, annulé)
- ✅ Actions sur les cours (confirmer, annuler, notes)
- ✅ Accès direct aux visioconférences

### Gestion des Disponibilités
- ✅ Planning hebdomadaire
- ✅ Création de créneaux
- ✅ Gestion par jour de la semaine
- ✅ Interface intuitive

### Système d'Annonces
- ✅ Création d'annonces multilingues
- ✅ Types: Promotion, Nouveau cours, Changements, etc.
- ✅ Ciblage par langue et niveau
- ✅ Statistiques d'engagement (vues, clics, réservations)
- ✅ Gestion des promotions et prix spéciaux

## 🔧 Configuration

### Base de Données
- **Type**: SQLite (développement)
- **Fichier**: `cms_db.sqlite3`
- **Migrations**: Appliquées automatiquement

### Environnement Virtuel
- **Répertoire**: `venv/`
- **Python**: 3.12
- **Packages**: Voir `requirements.txt`

## 🐛 Dépannage

### Problème d'Import Django
```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate
which python  # Doit pointer vers venv/bin/python
```

### Erreur de Migration
```bash
# Recréer les migrations
python manage.py makemigrations --empty [app_name]
python manage.py migrate --fake-initial
```

### Réinitialiser la Base de Données
```bash
# ATTENTION: Supprime toutes les données !
rm cms_db.sqlite3
python manage.py migrate
python create_superuser.py
```

## 📞 Support

Pour toute question ou problème :
1. Vérifiez que l'environnement virtuel est activé
2. Assurez-vous que toutes les migrations sont appliquées
3. Consultez les logs dans `cms.log` ou `cms_new.log`

## 🔄 Synchronisation avec le Backend

Le CMS est conçu pour synchroniser les données avec le backend principal :
- Les profils professeurs créés ici sont visibles côté étudiant
- Les réservations faites par les étudiants apparaissent dans le CMS
- Système de synchronisation bidirectionnel (à implémenter)