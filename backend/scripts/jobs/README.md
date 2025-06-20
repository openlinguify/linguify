# 💼 Scripts de Gestion des Jobs

Scripts pour gérer les candidatures et postes de travail.

## 📋 Scripts Disponibles

### `check_applications.py`
Vérifie les candidatures en production.
- **Usage**: `python scripts/jobs/check_applications.py`
- **Fonction**: Affiche les statistiques des candidatures et CVs
- **Environnement**: Production (change automatiquement)

## 🎯 Usage Typique

```bash
# Vérifier les candidatures
python scripts/jobs/check_applications.py

# Pour accéder aux CVs via admin
# 1. Changez DJANGO_ENV="production" dans .env
# 2. python manage.py runserver
# 3. http://localhost:8000/admin/jobs/jobapplication/
```

## 📊 Informations Affichées

- Nombre total de candidatures
- Candidatures avec/sans CV
- Répartition par statut
- Candidatures récentes
- Postes ouverts/fermés