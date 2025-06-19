# Quick Start - Créer un module Linguify

Guide rapide pour créer un nouveau module Linguify en 5 minutes.

## 🚀 Création rapide

```bash
# 1. Créer le module
./linguify-bin scaffold mon_module custom

# 2. Naviguer vers le module
cd custom/mon_module

# 3. Configurer le module
vi __manifest__.py

# 4. Voir la structure
ls -la
```

## 📁 Structure créée

```
mon_module/
├── __manifest__.py         # Configuration
├── README.md              # Documentation  
├── backend/apps/mon_module/    # Django app
└── frontend/src/addons/mon_module/  # React components
```

## ⚙️ Configuration de base (__manifest__.py)

```python
{
    'name': 'Mon Module',
    'version': '1.0.0',
    'category': 'Education/Language Learning', 
    'summary': 'Description courte',
    'depends': ['authentication', 'app_manager'],
    'installable': True,
    'application': True,
}
```

## 🔧 Intégration rapide

```bash
# Copier dans le projet principal
cp -r backend/apps/mon_module ../../backend/apps/
cp -r frontend/src/addons/mon_module ../../frontend/src/addons/

# Migrations
cd ../../backend
python manage.py makemigrations mon_module
python manage.py migrate
```

## 📖 Exemples de modules

```bash
# Module quiz avec icône Brain
./linguify-bin scaffold quiz custom --icon=Brain

# Module flashcards avec icône Zap  
./linguify-bin scaffold flashcards custom --icon=Zap

# Module bibliotheque avec icône BookOpen
./linguify-bin scaffold bibliotheque custom --icon=BookOpen
```

## 🎯 Accès rapide

Une fois intégré, votre module sera accessible à :
- **API** : `http://localhost:8000/api/v1/mon_module/`
- **Frontend** : `http://localhost:3000/mon_module`
- **Admin** : `http://localhost:8000/admin`

## 🛠️ Développement

1. **Backend** : Éditez `backend/apps/mon_module/models.py`
2. **Frontend** : Éditez `frontend/src/addons/mon_module/components/`
3. **API** : Éditez `backend/apps/mon_module/views.py`

## 📚 Documentation complète

→ Voir [linguify-module-generator.md](./linguify-module-generator.md) pour le guide complet.

---

**🎉 Votre module est prêt ! Bon développement !**