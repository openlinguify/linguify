"""
MANIFEST DU SYSTÈME DE TAGS GLOBAL LINGUIFY
==========================================

Vision: Un système unifié de tags cross-apps inspiré d'openlinguify base
Analogue au module "base" d'openlinguify, core contient les fonctionnalités fondamentales
partagées par toutes les applications Linguify.

## 🎯 OBJECTIF

Permettre aux utilisateurs de créer et gérer des tags qui fonctionnent 
à travers toutes les applications de l'écosystème Linguify :

- 📔 Notebook (notes)
- ✅ Todo (tâches et projets) 
- 📅 Calendar (événements)
- 🧠 Revision (decks de flashcards)
- 📄 Documents (fichiers et dossiers)
- 👥 Community (posts et discussions)

## 📊 MODÈLES DE DONNÉES

### Tag (Modèle principal)
- **ID**: UUID unique
- **User**: Propriétaire du tag
- **Name**: Nom du tag (unique par utilisateur, 1-50 caractères)
- **Color**: Couleur hexadécimale (#RRGGBB)
- **Description**: Description optionnelle (200 caractères max)
- **Usage counters**: Compteurs par app (notebook, todo, calendar, etc.)
- **Meta**: is_active, is_favorite, created_at, updated_at

### TagRelation (Relations génériques)
- **Tag**: Référence vers le tag
- **App name**: Nom de l'app (notebook, todo, etc.)
- **Model name**: Nom du modèle (Note, Task, Event, etc.)
- **Object ID**: ID de l'objet taggé
- **Created by**: Utilisateur qui a créé la relation
- **Created at**: Date de création

## 🔌 API REST

### Tags Endpoints
- `GET /api/v1/core/tags/` - Liste des tags utilisateur
- `POST /api/v1/core/tags/` - Créer un nouveau tag
- `GET /api/v1/core/tags/{id}/` - Détails d'un tag
- `PUT /api/v1/core/tags/{id}/` - Modifier un tag
- `DELETE /api/v1/core/tags/{id}/` - Supprimer un tag
- `GET /api/v1/core/tags/popular/` - Tags populaires et suggestions
- `GET /api/v1/core/tags/search/` - Recherche avancée
- `POST /api/v1/core/tags/{id}/toggle_favorite/` - Basculer favori
- `POST /api/v1/core/tags/{id}/toggle_active/` - Basculer actif
- `GET /api/v1/core/tags/{id}/usage_stats/` - Statistiques détaillées

### Object Tags Endpoints
- `GET /api/v1/core/object-tags/get_object_tags/` - Tags d'un objet
- `POST /api/v1/core/object-tags/set_object_tags/` - Définir les tags d'un objet
- `POST /api/v1/core/object-tags/add_tag_to_object/` - Ajouter un tag
- `DELETE /api/v1/core/object-tags/remove_tag_from_object/` - Retirer un tag

### Relations Endpoints
- `GET /api/v1/core/tag-relations/` - Liste des relations
- `POST /api/v1/core/tag-relations/` - Créer une relation
- `DELETE /api/v1/core/tag-relations/{id}/` - Supprimer une relation

## 🛠 UTILISATION DANS LES APPS

### Exemple d'usage dans une app

```python
from core.models.tags import Tag, add_tag_to_object, get_tags_for_object

# Dans une vue Django (ex: notebook)
def add_tags_to_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    tag_ids = request.data.get('tag_ids', [])
    
    for tag_id in tag_ids:
        tag = get_object_or_404(Tag, id=tag_id, user=request.user)
        add_tag_to_object(tag, 'notebook', 'Note', note.id, request.user)
    
    # Récupérer les tags de la note
    tags = get_tags_for_object('notebook', 'Note', note.id, request.user)
    return Response(TagListSerializer(tags, many=True).data)
```

### Exemple d'usage en JavaScript

```javascript
// Client API pour gérer les tags
class LinguifyTagsAPI {
    async getTags(filters = {}) {
        const params = new URLSearchParams(filters);
        return fetch(`/api/v1/core/tags/?${params}`);
    }
    
    async setObjectTags(appName, modelName, objectId, tagIds) {
        return fetch('/api/v1/core/object-tags/set_object_tags/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                app_name: appName,
                model_name: modelName,
                object_id: objectId,
                tag_ids: tagIds
            })
        });
    }
}
```

## 🎨 INTERFACE UTILISATEUR

### Composant Tags Management Modal
- Interface unifiée pour gérer tous les tags
- Création/édition avec aperçu en temps réel
- Sélecteur de couleurs avec presets
- Recherche et filtrage
- Statistiques d'usage par app

### Intégration dans les apps
Chaque app peut inclure le système de tags via :
- `{% include 'core/components/tags-selector.html' %}`
- JavaScript: `window.linguifyTags.init()`

## 📈 ANALYTICS & STATISTIQUES

- Compteurs d'usage automatiques par app
- Identification de l'app principale pour chaque tag  
- Historique des utilisations
- Suggestions basées sur l'usage

## 🔒 SÉCURITÉ

- Tags isolés par utilisateur (user-scoped)
- Validation des permissions dans toutes les APIs
- Protection contre les injections dans les noms de tags
- Limitation des taux de création

## 🚀 MIGRATION

### Depuis les systèmes existants
1. **Notebook tags** → Tags globaux
2. **Todo tags** → Tags globaux  
3. **Autres apps** → Utilisation directe du système global

### Script de migration
```python
# Migrer les tags existants vers le système global
python manage.py migrate_to_global_tags
```

## 📝 ROADMAP

- [ ] Interface web de gestion complète
- [ ] Tags partagés entre utilisateurs
- [ ] Tags sugérés par IA
- [ ] Import/Export de tags
- [ ] Synchronisation cross-device
- [ ] Système de templates de tags

## 🧪 TESTS

Tests couvrant :
- Modèles et validations
- APIs REST complètes
- Relations cross-apps
- Interface utilisateur
- Performance avec grandes quantités

---

Ce système de tags global suit la philosophie Linguify :
**Simple, Puissant, Cross-Apps, Centré sur l'Utilisateur**
"""