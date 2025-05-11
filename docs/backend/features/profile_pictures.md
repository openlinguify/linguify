# Gestion des Photos de Profil

> **Mise à jour importante**: Le système de stockage des photos de profil a été mis à jour. Voir la section [Migration](#migration-des-photos-existantes) pour plus d'informations sur la transition des photos existantes.

## Introduction

Linguify implémente un système de gestion des photos de profil inspiré des réseaux sociaux modernes. Ce système offre:

- **Organisation efficace**: Photos organisées par utilisateur
- **Versions multiples**: Différentes tailles pour différents contextes d'affichage
- **Conservation d'historique**: Versions précédentes conservées pour référence et possibilité de restauration
- **Optimisation automatique**: Compression et redimensionnement pour économiser de l'espace et du temps de chargement

## Structure des Fichiers

```
/media/profiles/
   /{user_id}/               # ID de l'utilisateur ou 'temp'
      /original/             # Fichiers originaux uploadés 
         /{timestamp}_{uuid}.jpg
      /optimized/            # Version optimisée pour l'affichage
         /{uuid}.jpg
      /thumbnails/           # Vignettes pour différents contextes
         /small_{uuid}.jpg   # Petite (50x50px) - Commentaires, notifications
         /medium_{uuid}.jpg  # Moyenne (150x150px) - Cartes profil, listes
         /large_{uuid}.jpg   # Grande (300x300px) - Pages profil
```

## Composants Principaux

### 1. Stockage des Images (`ProfileStorage`)

- Classe de stockage Django personnalisée dans `apps.authentication.storage`
- Gère l'organisation des fichiers, la génération des vignettes et l'optimisation
- Maintient l'historique des photos en conservant les originaux avec un horodatage

### 2. Utilitaires d'Accès (`helpers.py`)

- `get_profile_picture_urls(user)`: Obtient les URLs pour toutes les tailles d'une photo de profil
- `get_profile_picture_html(user, size)`: Génère le HTML pour afficher la photo avec chargement progressif
- `get_default_profile_picture()`: Renvoie les URLs des images par défaut
- `invalidate_profile_picture_cache(user_id)`: Rafraîchit le cache après modification
- `clean_temp_profile_pictures(max_age)`: Nettoie les fichiers temporaires

### 3. Commandes de Maintenance

- `python manage.py create_profile_directories`: Crée la structure de répertoires
- `python manage.py cleanup_profile_pictures`: Nettoie les fichiers temporaires et historiques

## Utilisation

### Dans les Templates Django

```django
{% load profile_helpers %}

<!-- Affichage simple -->
{{ user|profile_picture:"medium" }}

<!-- Avec classes CSS personnalisées -->
{{ user|profile_picture:"small"|add_class:"rounded-circle" }}

<!-- Affichage conditionnel -->
{% if user.profile_picture %}
    {{ user|profile_picture:"large" }}
{% else %}
    <span class="avatar-placeholder">{{ user.initials }}</span>
{% endif %}
```

### Dans les API REST

```python
from apps.authentication.helpers import get_profile_picture_urls

@api_view(['GET'])
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return Response({
        'id': user.id,
        'name': user.name,
        'profile_pictures': get_profile_picture_urls(user),
        # Autres champs...
    })
```

### Upload d'une Nouvelle Photo

```python
from apps.authentication.helpers import invalidate_profile_picture_cache

@api_view(['POST'])
def update_profile_picture(request):
    # Traitement du fichier uploadé
    if 'photo' in request.FILES:
        request.user.profile_picture = request.FILES['photo']
        request.user.save()
        
        # Invalider le cache
        invalidate_profile_picture_cache(request.user.id)
        
        return Response({'success': True})
    
    return Response({'error': 'No photo provided'}, status=400)
```

## Configuration

Dans `settings.py`:

```python
# Tailles d'images pour différents contextes
PROFILE_PICTURE_SIZES = {
    'small': (50, 50),       # Pour commentaires, notifications
    'medium': (150, 150),    # Pour les cartes profil
    'large': (300, 300),     # Pour la page profil
}

# Paramètres de qualité et format
PROFILE_PICTURE_QUALITY = 85       # Qualité JPEG (1-100)
PROFILE_PICTURE_FORMAT = 'JPEG'    # Format par défaut
PROFILE_PICTURE_MAX_DISPLAY_SIZE = (800, 800)  # Dimensions max

# Validation des images téléchargées
PROFILE_PICTURE_MAX_SIZE = 5 * 1024 * 1024  # Taille max 5MB
PROFILE_PICTURE_MIN_WIDTH = 200    # Largeur minimale
PROFILE_PICTURE_MIN_HEIGHT = 200   # Hauteur minimale

# Comportement de stockage
PROFILE_PICTURE_KEEP_ORIGINALS = True     # Conserver les fichiers originaux
PROFILE_PICTURE_MAX_VERSIONS = 5          # Nombre de versions à conserver
```

## Maintenance

Pour éviter l'accumulation de fichiers temporaires et d'anciennes versions, exécutez régulièrement:

```bash
# Nettoyage manuel
python manage.py cleanup_profile_pictures --days=30 --temp-hours=24

# Via une tâche cron (recommandé)
0 3 * * * cd /path/to/project && python manage.py cleanup_profile_pictures --force
```

## Performance et Optimisations

- **Mise en cache**: Les URLs sont mises en cache pour réduire les accès disque
- **Chargement progressif**: Les templates génèrent du HTML avec attributs data pour chargement progressif
- **Purge automatique**: Les fichiers temporaires sont nettoyés automatiquement
- **Conservation limitée**: Seules les N dernières versions sont conservées

## Migration des Photos Existantes

Le système a été mis à jour pour passer d'un stockage simple (`/media/profile_pictures/*.jpg`) à une organisation plus structurée. Les modifications comprennent:

1. Ajout de la compatibilité avec l'ancien format
2. Script de migration pour déplacer les anciennes photos vers le nouveau système
3. Gestion automatique des deux formats

### Exécution de la Migration

Pour migrer les photos existantes vers le nouveau format:

```bash
# Migrer toutes les photos de profil
python manage.py migrate_profile_pictures

# Migrer un utilisateur spécifique
python manage.py migrate_profile_pictures --user-id=123

# Simuler la migration sans effectuer les modifications
python manage.py migrate_profile_pictures --dry-run
```

### État de la Migration

- Les utilisateurs ayant des photos dans l'ancien format continueront de voir leur photo
- Ces photos s'afficheront à une seule taille (pas de vignettes automatiques)
- Lors de la mise à jour d'une photo, elle sera automatiquement migrée vers le nouveau format

## Considérations Futures

- Support du format WebP pour réduire davantage la taille des images
- Détection de visage pour un recadrage intelligent des photos
- Interface admin pour gérer les photos des utilisateurs
- Option de restauration des versions précédentes
- Migration complète des anciennes photos vers le nouveau système