import os
import glob
import time
import json
from django.conf import settings
import logging
from django.core.cache import cache
from django.utils.html import mark_safe
from django.templatetags.static import static

logger = logging.getLogger(__name__)

def get_profile_picture_urls(user, use_cache=True):
    """
    Obtient les URLs pour toutes les versions de la photo de profil d'un utilisateur.

    Args:
        user: L'instance User dont on veut les photos
        use_cache: Si True, utilise le cache pour éviter des recherches répétées

    Returns:
        dict: Dictionnaire avec les URLs pour chaque taille (small, medium, large, optimized, original)
        ou None si l'utilisateur n'a pas de photo de profil
    """
    # Utiliser une image par défaut si l'utilisateur n'a pas de photo
    if not user:
        return get_default_profile_picture()

    # Priorité à Supabase Storage
    if hasattr(user, 'profile_picture_url') and user.profile_picture_url:
        # Si l'utilisateur a une URL Supabase, l'utiliser directement
        return {
            'default': user.profile_picture_url,
            'small': user.profile_picture_url,
            'medium': user.profile_picture_url,
            'large': user.profile_picture_url,
            'optimized': user.profile_picture_url,
            'original': user.profile_picture_url,
            'supabase': True  # Marquer comme provenant de Supabase
        }

    if not user.profile_picture:
        return get_default_profile_picture()

    # Vérifier si les URLs sont en cache
    if use_cache:
        cache_key = f"profile_pic_urls_{user.id}_{user.updated_at.timestamp()}"
        cached_urls = cache.get(cache_key)
        if cached_urls:
            return cached_urls

    # URL de base depuis la photo de profil principale
    base_url = user.profile_picture.url
    profile_picture_path = str(user.profile_picture)

    # --- SUPPORT DE L'ANCIEN FORMAT ---
    # Si c'est une ancienne photo de profil (format: profile_pictures/FILENAME.jpg)
    if 'profile_pictures' in profile_picture_path:
        # Renvoyer un format simplifié pour les anciennes photos
        result = {
            'default': base_url,
            'small': base_url,
            'medium': base_url,
            'large': base_url,
            'optimized': base_url,
            'legacy': True  # Marquer comme ancien format
        }

        # Mettre en cache pour 1 heure (3600 secondes)
        if use_cache:
            cache.set(cache_key, result, 3600)

        return result

    # L'URL principale correspond à la version optimisée
    # Format typique: /media/profiles/USER_ID/optimized/UUID.jpg
    try:
        # Extraire les parties du chemin
        parts = os.path.normpath(base_url).split(os.sep)

        # Chercher l'ID utilisateur et le nom de fichier
        profiles_index = None
        user_id = None
        filename = None

        for i, part in enumerate(parts):
            if part == 'profiles' and profiles_index is None:
                profiles_index = i
            elif profiles_index is not None and i == profiles_index + 1 and user_id is None:
                # L'ID utilisateur suit directement 'profiles'
                user_id = part
            elif part == 'optimized' and user_id is not None:
                if i + 1 < len(parts):
                    filename = parts[i+1]  # Le nom du fichier est juste après 'optimized'

        # Si on a trouvé tous les éléments nécessaires
        if profiles_index is not None and user_id is not None and filename is not None:
            # Construire les chemins de base
            media_url = '/'.join(parts[:profiles_index])  # /media
            profiles_path = f"{media_url}/profiles"

            # Extraire l'UUID et l'extension
            uuid_ext = filename  # uuid.ext
            uuid_part, ext = os.path.splitext(uuid_ext)  # Séparer uuid et extension

            # Résultat avec toutes les URLs
            result = {
                'default': base_url,
                'optimized': base_url,
                'timestamp': int(time.time()),  # Ajouter un timestamp pour invalidation
            }

            # Rechercher l'original s'il existe (format: timestamp_uuid.ext)
            # Utiliser le glob pour trouver les fichiers correspondants
            original_pattern = os.path.join(settings.MEDIA_ROOT, 'profiles', user_id, 'original', f"*_{uuid_part}{ext}")
            original_files = glob.glob(original_pattern)

            if original_files:
                # Prendre le fichier le plus récent
                original_file = sorted(original_files, reverse=True)[0]
                original_filename = os.path.basename(original_file)
                result['original'] = f"{profiles_path}/{user_id}/original/{original_filename}"

            # Ajouter les URLs pour toutes les tailles de vignettes
            for size in ['small', 'medium', 'large']:
                result[size] = f"{profiles_path}/{user_id}/thumbnails/{size}_{uuid_part}{ext}"

            # Mettre en cache pour 1 heure (3600 secondes)
            if use_cache:
                cache.set(cache_key, result, 3600)

            return result
    except Exception as e:
        logger.error(f"Erreur lors de la génération des URLs de photo de profil: {e}")

    # En cas d'erreur, renvoyer juste l'URL principale
    return {'default': base_url}


def get_default_profile_picture():
    """
    Renvoie l'URL d'une image de profil par défaut.
    """
    return {
        'default': static('images/default-profile.png'),
        'small': static('images/default-profile-small.png'),
        'medium': static('images/default-profile-medium.png'),
        'large': static('images/default-profile-large.png'),
        'optimized': static('images/default-profile.png'),
        'is_default': True
    }


def get_profile_picture_html(user, size='medium', css_class='', alt=''):
    """
    Génère le HTML pour afficher l'image de profil d'un utilisateur.

    Args:
        user: L'utilisateur dont on veut afficher la photo
        size: Taille de l'image ('small', 'medium', 'large')
        css_class: Classes CSS additionnelles
        alt: Texte alternatif

    Returns:
        Chaîne HTML sécurisée pour l'affichage de l'image
    """
    urls = get_profile_picture_urls(user)

    if not alt and user:
        alt = f"Photo de profil de {user.name}" if hasattr(user, 'name') else "Photo de profil"

    # S'assurer que la taille demandée existe, sinon utiliser 'default'
    img_url = urls.get(size, urls.get('default'))

    # Construire le HTML avec toutes les classes et attributs nécessaires
    html = f'<img src="{img_url}" alt="{alt}" class="profile-picture {size} {css_class}"'

    # Ajouter des attributs data pour un chargement progressif en frontend
    if 'small' in urls and 'medium' in urls and 'large' in urls:
        html += f' data-small="{urls["small"]}" data-medium="{urls["medium"]}" data-large="{urls["large"]}"'

    html += ' />'

    # Marquer comme sécurisé pour éviter l'échappement
    return mark_safe(html)


def invalidate_profile_picture_cache(user_id):
    """
    Invalide le cache des URLs de photo de profil pour un utilisateur.
    À appeler après une mise à jour de photo.
    """
    pattern = f"profile_pic_urls_{user_id}_*"
    # Django ne supporte pas le pattern matching pour la suppression de cache,
    # donc on doit simuler avec une liste de clés
    keys_to_delete = []
    for key in cache._cache.keys():
        if isinstance(key, str) and key.startswith(f"profile_pic_urls_{user_id}_"):
            keys_to_delete.append(key)

    for key in keys_to_delete:
        cache.delete(key)


def clean_temp_profile_pictures(max_age=86400):
    """
    Nettoie les photos de profil temporaires plus anciennes que max_age secondes.

    Args:
        max_age: Âge maximum en secondes (par défaut: 24h)

    Returns:
        dict: Statistiques de nettoyage
    """
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'profiles', 'temp')
    if not os.path.exists(temp_dir):
        return {"status": "skipped", "reason": "temp directory not found"}

    now = time.time()
    deleted_count = 0
    error_count = 0

    # Parcourir tous les sous-répertoires (original, optimized, thumbnails)
    for subdir in ['original', 'optimized', 'thumbnails']:
        subdir_path = os.path.join(temp_dir, subdir)
        if not os.path.exists(subdir_path):
            continue

        # Parcourir tous les fichiers
        for filename in os.listdir(subdir_path):
            file_path = os.path.join(subdir_path, filename)

            # Vérifier l'âge du fichier
            try:
                file_stat = os.stat(file_path)
                file_age = now - file_stat.st_mtime

                if file_age > max_age:
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du fichier {file_path}: {e}")
                error_count += 1

    return {
        "status": "completed",
        "deleted_count": deleted_count,
        "error_count": error_count
    }