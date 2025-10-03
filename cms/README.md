# Linguify Teacher CMS

CMS pour les enseignants de la plateforme Linguify - Création et gestion de contenu éducatif.

## 🎯 Objectif

Le CMS permet aux enseignants de :
- ✅ Créer et gérer leurs cours (Units, Chapters, Lessons)
- ✅ Gérer leur profil et qualifications
- ✅ Suivre leurs revenus et ventes
- ✅ Planifier leurs cours particuliers
- ✅ Synchroniser leur contenu vers le Backend étudiant

## 🏗️ Architecture

```
cms/
├── apps/
│   ├── core/            # Modèles de base et dashboard
│   ├── teachers/        # Gestion profils enseignants
│   ├── course_builder/  # Création de contenu
│   ├── monetization/    # Revenus et paiements
│   ├── scheduling/      # Planning cours particuliers
│   └── sync/           # Synchronisation vers Backend
├── templates/          # Templates HTML
└── static/            # Fichiers statiques
```

## 🚀 Installation

1. **Initialisation automatique :**
```bash
./init_cms.sh
```

2. **Installation manuelle :**
```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
createdb linguify_cms
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

## 🎮 Usage

### Démarrer le serveur
```bash
# Depuis la racine du projet
make cms

# Ou directement
cd cms && python manage.py runserver 8002
```

### Accès
- **Interface CMS :** http://127.0.0.1:8002/
- **Admin Django :** http://127.0.0.1:8002/admin/

## 📊 Fonctionnalités

### 👨‍🏫 Gestion Enseignants
- Profils avec biographie multilingue
- Qualifications et certifications
- Langues enseignées avec niveaux
- Disponibilités hebdomadaires

### 📚 Création de Contenu
- **Units :** Cours principaux avec niveaux (A1-C2)
- **Chapters :** Chapitres thématiques
- **Lessons :** Leçons individuelles
- **Content :** Vocabulaire, théorie, exercices

### 💰 Monétisation
- Suivi des ventes en temps réel
- Calcul automatique des commissions (15%)
- Demandes de paiement
- Historique des revenus

### 🗓️ Planning
- Cours particuliers avec étudiants
- Gestion des créneaux disponibles
- Intégration vidéo (Zoom/Meet)

### 🔄 Synchronisation
- API REST vers Backend étudiant
- Statuts de sync (Draft/Pending/Synced/Failed)
- Synchronisation automatique ou manuelle

## 🛠️ Développement

### Structure des Modèles
```python
# Héritage commun
class SyncableModel(TimestampedModel):
    sync_status = CharField(choices=SyncStatus.choices)
    backend_id = PositiveIntegerField()
    # ...

# Exemple Unit
class CMSUnit(SyncableModel, MultilingualMixin):
    teacher = ForeignKey(Teacher)
    title_en/fr/es/nl = CharField()
    level = CharField(choices=LEVEL_CHOICES)
    price = DecimalField()
    # ...
```

### API de Synchronisation
```python
# Services de sync
sync_service = BackendSyncService()
sync_service.sync_unit(cms_unit)
sync_service.sync_teacher(teacher)

# Endpoints
POST /api/sync/sync-all/        # Sync tout le contenu
POST /api/sync/sync-unit/123/   # Sync unit spécifique
GET  /api/sync/status/          # Statut sync
```

## 🔗 Intégration Backend

Le CMS communique avec le Backend étudiant via API REST :
- **Endpoint Backend :** `http://127.0.0.1:8081/api/`
- **Authentification :** Token-based
- **Format :** JSON

## 📋 Todo

- [ ] Interface graphique de création de contenu
- [ ] Éditeur WYSIWYG pour théorie
- [ ] Upload d'images et audio
- [ ] Analytics avancées
- [ ] Notifications en temps réel
- [ ] API webhooks pour sync bidirectionnelle

## 🐛 Dépannage

### Erreurs communes

**Sync failed:**
```bash
# Vérifier la connectivité Backend
curl http://127.0.0.1:8081/api/
```

**Base de données:**
```bash
# Recréer les migrations
python manage.py makemigrations --empty core
python manage.py migrate
```

## 📞 Support

Pour le support technique, contactez l'équipe de développement Linguify.