"""
Module de gestion centralisée des profils utilisateur.
Regroupe toutes les fonctionnalités liées aux profils dans un seul module.
"""

import os
import glob
import uuid
import time
import shutil
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.utils import timezone
from django.templatetags.static import static

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Formats d'image supportés
SUPPORTED_IMAGE_FORMATS = {
    'jpeg': 'JPEG',
    'jpg': 'JPEG',
    'png': 'PNG',
    'webp': 'WEBP',
    'gif': 'PNG',  # On convertit GIF en PNG
}

# Formats d'image préférés pour l'optimisation
PREFERRED_FORMAT = 'JPEG'
DEFAULT_QUALITY = 85

# Tailles des vignettes
DEFAULT_SIZES = {
    'small': (50, 50),      # Pour commentaires, notifications
    'medium': (150, 150),   # Pour les cartes profil
    'large': (300, 300),    # Pour la page profil
}

# Taille maximale pour les fichiers optimisés
MAX_SIZE = (800, 800)

# Nombre maximal de versions historiques à conserver
MAX_VERSIONS = 5

# Chemins par défaut
LEGACY_DIR = 'profile_pictures'
PROFILES_DIR = 'profiles'

# -----------------------------------------------------------------------------
# Core Image Processing Functions
# -----------------------------------------------------------------------------

def optimize_image(img: Image.Image, 
                  max_size: Tuple[int, int] = MAX_SIZE, 
                  format: str = PREFERRED_FORMAT, 
                  quality: int = DEFAULT_QUALITY) -> bytes:
    """
    Optimise une image PIL pour le stockage web.
    
    Args:
        img: L'image PIL à optimiser
        max_size: La taille maximale (largeur, hauteur)
        format: Le format de sortie (JPEG, PNG, WEBP)
        quality: La qualité pour JPEG et WEBP (1-100)
        
    Returns:
        bytes: L'image optimisée au format binaire
    """
    # Cloner l'image pour ne pas modifier l'original
    img_copy = img.copy()
    
    # Convertir en RGB si nécessaire
    if img_copy.mode in ('RGBA', 'LA') and format == 'JPEG':
        # Pour JPEG, convertir RGBA en RGB avec fond blanc
        background = Image.new('RGB', img_copy.size, (255, 255, 255))
        background.paste(img_copy, mask=img_copy.split()[3] if img_copy.mode == 'RGBA' else None)
        img_copy = background
    elif img_copy.mode != 'RGB' and format in ('JPEG', 'WEBP'):
        img_copy = img_copy.convert('RGB')
    
    # Auto-rotation basée sur EXIF
    try:
        img_copy = ImageOps.exif_transpose(img_copy)
    except Exception as e:
        logger.warning(f"Impossible d'appliquer la rotation EXIF: {e}")
    
    # Redimensionner si nécessaire
    if img_copy.width > max_size[0] or img_copy.height > max_size[1]:
        img_copy.thumbnail(max_size, Image.LANCZOS)
    
    # Exporter l'image optimisée
    buffer = BytesIO()
    
    # Paramètres d'enregistrement selon le format
    save_params = {
        'format': format,
    }
    
    if format in ('JPEG', 'WEBP'):
        save_params['quality'] = quality
        save_params['optimize'] = True
        
    if format == 'PNG':
        save_params['optimize'] = True
    
    img_copy.save(buffer, **save_params)
    return buffer.getvalue()


def create_thumbnails(img: Image.Image, 
                     sizes: Dict[str, Tuple[int, int]] = DEFAULT_SIZES, 
                     format: str = PREFERRED_FORMAT, 
                     quality: int = DEFAULT_QUALITY) -> Dict[str, bytes]:
    """
    Crée différentes tailles de vignettes pour une image.
    
    Args:
        img: L'image PIL source
        sizes: Dictionnaire des tailles {nom: (largeur, hauteur)}
        format: Le format de sortie
        quality: La qualité (1-100)
        
    Returns:
        Dict[str, bytes]: Un dictionnaire {nom_taille: image_bytes}
    """
    result = {}
    
    for size_name, dimensions in sizes.items():
        # Optimiser avec les dimensions spécifiques
        thumb_data = optimize_image(img, dimensions, format, quality)
        result[size_name] = thumb_data
    
    return result


def process_profile_picture(image_data: bytes, 
                           user_id: Union[int, str] = 'temp', 
                           format: str = PREFERRED_FORMAT) -> Dict[str, Dict[str, Any]]:
    """
    Traite une photo de profil complètement (optimisation + vignettes).
    
    Args:
        image_data: Les données binaires de l'image
        user_id: L'ID de l'utilisateur ou 'temp'
        format: Le format de sortie
    
    Returns:
        Dict: Informations sur les images générées
    """
    # Ouvrir l'image
    img = Image.open(BytesIO(image_data))
    
    # Générer un ID unique et l'horodatage
    unique_id = uuid.uuid4().hex
    timestamp = int(time.time())
    
    # Déterminer l'extension basée sur le format
    ext = '.jpg' if format == 'JPEG' else f'.{format.lower()}'
    
    # Préparer les résultats
    result = {
        'metadata': {
            'user_id': user_id,
            'unique_id': unique_id,
            'timestamp': timestamp,
            'format': format,
            'original_size': (img.width, img.height),
            'extension': ext,
        },
        'images': {
            'original': {
                'data': image_data,
                'path': f"{PROFILES_DIR}/{user_id}/original/{timestamp}_{unique_id}{ext}",
            },
        }
    }
    
    # Optimiser l'image principale
    optimized_data = optimize_image(img, MAX_SIZE, format, DEFAULT_QUALITY)
    result['images']['optimized'] = {
        'data': optimized_data,
        'path': f"{PROFILES_DIR}/{user_id}/optimized/{unique_id}{ext}",
    }
    
    # Créer les vignettes
    thumbnails = create_thumbnails(img, DEFAULT_SIZES, format, DEFAULT_QUALITY)
    for size_name, thumb_data in thumbnails.items():
        result['images'][size_name] = {
            'data': thumb_data,
            'path': f"{PROFILES_DIR}/{user_id}/thumbnails/{size_name}_{unique_id}{ext}",
        }
    
    return result


# -----------------------------------------------------------------------------
# File System Operations
# -----------------------------------------------------------------------------

def ensure_profile_directories(user_id: Union[int, str] = 'temp') -> Dict[str, str]:
    """
    Crée les répertoires nécessaires pour les photos de profil d'un utilisateur.
    
    Args:
        user_id: L'ID de l'utilisateur ou 'temp'
    
    Returns:
        Dict[str, str]: Un dictionnaire des chemins créés
    """
    user_dir = os.path.join(settings.MEDIA_ROOT, PROFILES_DIR, str(user_id))
    
    paths = {
        'user': user_dir,
        'original': os.path.join(user_dir, 'original'),
        'optimized': os.path.join(user_dir, 'optimized'),
        'thumbnails': os.path.join(user_dir, 'thumbnails'),
    }
    
    for path_name, path in paths.items():
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
    
    return paths


def save_processed_images(processed_data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """
    Enregistre les images traitées sur le disque.
    
    Args:
        processed_data: Les données générées par process_profile_picture
    
    Returns:
        Dict[str, str]: Dictionnaire des chemins enregistrés
    """
    user_id = processed_data['metadata']['user_id']
    
    # S'assurer que les répertoires existent
    ensure_profile_directories(user_id)
    
    saved_paths = {}
    
    # Sauvegarder chaque image
    for image_type, image_info in processed_data['images'].items():
        full_path = os.path.join(settings.MEDIA_ROOT, image_info['path'])
        
        # Sauvegarder le fichier
        with open(full_path, 'wb') as f:
            f.write(image_info['data'])
        
        saved_paths[image_type] = image_info['path']
    
    return saved_paths


def clean_old_versions(user_id: Union[int, str], max_versions: int = MAX_VERSIONS) -> int:
    """
    Supprime les anciennes versions des photos de profil.
    
    Args:
        user_id: L'ID de l'utilisateur
        max_versions: Nombre maximal de versions à conserver
    
    Returns:
        int: Nombre de fichiers supprimés
    """
    original_dir = os.path.join(settings.MEDIA_ROOT, PROFILES_DIR, str(user_id), 'original')
    
    if not os.path.exists(original_dir):
        return 0
    
    # Lister et trier les fichiers par date (décroissant)
    files = []
    for filename in os.listdir(original_dir):
        file_path = os.path.join(original_dir, filename)
        if os.path.isfile(file_path):
            try:
                # Les noms sont au format: timestamp_uuid.ext
                timestamp = int(filename.split('_')[0])
            except (ValueError, IndexError):
                # Utiliser la date de modification si le format ne correspond pas
                timestamp = int(os.path.getmtime(file_path))
            
            files.append((file_path, timestamp, filename))
    
    # Trier par timestamp (plus récent en premier)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Supprimer les versions au-delà de la limite
    deleted_count = 0
    for file_path, _, _ in files[max_versions:]:
        try:
            os.remove(file_path)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {file_path}: {e}")
    
    return deleted_count


def migrate_legacy_profile_picture(user_model,
                                 legacy_path: str, 
                                 user_id: Union[int, str]) -> Optional[str]:
    """
    Migre une photo de profil du format legacy vers le nouveau format.
    
    Args:
        user_model: L'instance du modèle utilisateur
        legacy_path: Le chemin relatif de l'ancienne photo
        user_id: L'ID de l'utilisateur
    
    Returns:
        Optional[str]: Le nouveau chemin relatif, ou None en cas d'erreur
    """
    # Chemin complet de l'ancien fichier
    full_legacy_path = os.path.join(settings.MEDIA_ROOT, legacy_path)
    
    if not os.path.exists(full_legacy_path):
        logger.warning(f"Fichier legacy introuvable: {full_legacy_path}")
        return None
    
    try:
        # Lire les données du fichier
        with open(full_legacy_path, 'rb') as f:
            image_data = f.read()
        
        # Déterminer le format basé sur l'extension
        _, ext = os.path.splitext(legacy_path)
        ext = ext.lower().lstrip('.')
        format_name = SUPPORTED_IMAGE_FORMATS.get(ext, PREFERRED_FORMAT)
        
        # Traiter l'image
        processed = process_profile_picture(image_data, user_id, format_name)
        
        # Sauvegarder les images
        saved_paths = save_processed_images(processed)
        
        # Mettre à jour le modèle utilisateur
        with transaction.atomic():
            user_model.profile_picture = saved_paths['optimized']
            user_model.save(update_fields=['profile_picture'])
        
        # Nettoyer les anciennes versions
        clean_old_versions(user_id)
        
        return saved_paths['optimized']
    
    except Exception as e:
        logger.error(f"Erreur lors de la migration de {legacy_path}: {e}")
        return None


# -----------------------------------------------------------------------------
# URL & HTML Helpers
# -----------------------------------------------------------------------------

def get_profile_picture_urls(user, use_cache: bool = True) -> Dict[str, str]:
    """
    Obtient toutes les URLs pour les différentes versions de la photo de profil.
    
    Args:
        user: L'instance User
        use_cache: Utiliser le cache pour les résultats
    
    Returns:
        Dict[str, str]: Dictionnaire des URLs
    """
    # Vérifier si l'utilisateur existe et a une photo
    if not user:
        return get_default_profile_picture()
    
    if not hasattr(user, 'profile_picture') or not user.profile_picture:
        return get_default_profile_picture()
    
    # Utiliser le cache si disponible
    if use_cache:
        cache_key = f"profile_pic_urls_{user.id}_{user.updated_at.timestamp()}"
        cached_urls = cache.get(cache_key)
        if cached_urls:
            return cached_urls
    
    profile_picture_path = str(user.profile_picture)
    base_url = user.profile_picture.url
    
    # Gérer le format legacy (profile_pictures/...)
    if profile_picture_path.startswith(LEGACY_DIR) or LEGACY_DIR in profile_picture_path:
        legacy_result = {
            'default': base_url,
            'small': base_url,
            'medium': base_url,
            'large': base_url,
            'optimized': base_url,
            'legacy': True,
            'timestamp': int(time.time()),
        }
        
        if use_cache:
            cache.set(cache_key, legacy_result, 3600)
        
        return legacy_result
    
    # Gérer le nouveau format (profiles/USER_ID/...)
    try:
        # Extraire les parties du chemin
        parts = Path(profile_picture_path).parts
        
        # Chercher l'ID utilisateur et le nom de fichier
        user_id = None
        filename = None
        
        for i, part in enumerate(parts):
            if part == PROFILES_DIR and i + 1 < len(parts):
                user_id = parts[i + 1]
            elif part == 'optimized' and i + 1 < len(parts):
                filename = parts[i + 1]
        
        if not user_id or not filename:
            raise ValueError(f"Format de chemin non reconnu: {profile_picture_path}")
        
        # Extraire l'UUID et l'extension pour construire les autres chemins
        uuid_part, ext = os.path.splitext(filename)
        
        # Construire les URLs relatives pour toutes les tailles
        media_url = settings.MEDIA_URL.rstrip('/')
        result = {
            'default': base_url,
            'optimized': base_url,
            'timestamp': int(time.time()),
        }
        
        # Ajouter les URLs des vignettes
        for size in DEFAULT_SIZES:
            result[size] = f"{media_url}/{PROFILES_DIR}/{user_id}/thumbnails/{size}_{uuid_part}{ext}"
        
        # Rechercher l'original (peut avoir un timestamp différent)
        original_pattern = os.path.join(
            settings.MEDIA_ROOT, PROFILES_DIR, str(user_id), 
            'original', f"*_{uuid_part}{ext}"
        )
        original_files = glob.glob(original_pattern)
        
        if original_files:
            original_file = sorted(original_files, reverse=True)[0]
            original_filename = os.path.basename(original_file)
            result['original'] = f"{media_url}/{PROFILES_DIR}/{user_id}/original/{original_filename}"
        
        # Mettre en cache
        if use_cache:
            cache.set(cache_key, result, 3600)
        
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération des URLs: {e}")
        
        # En cas d'erreur, renvoyer un format simplifié
        return {'default': base_url}


def get_default_profile_picture() -> Dict[str, str]:
    """
    Renvoie les URLs pour les images de profil par défaut.
    
    Returns:
        Dict[str, str]: Dictionnaire des URLs par défaut
    """
    result = {
        'default': static('images/default-profile.png'),
        'small': static('images/default-profile-small.png'),
        'medium': static('images/default-profile-medium.png'),
        'large': static('images/default-profile-large.png'),
        'optimized': static('images/default-profile.png'),
        'is_default': True
    }
    
    # Vérifier si les fichiers existent et utiliser un fallback si nécessaire
    for key in list(result.keys()):
        if key != 'is_default':
            path = os.path.join(settings.STATIC_ROOT, 'images', f"default-profile{'-' + key if key != 'default' else ''}.png")
            if not os.path.exists(path):
                result[key] = result['default']
    
    return result


def get_profile_picture_html(user, size='medium', css_class='', alt=''):
    """
    Génère le HTML pour une image de profil avec chargement progressif.
    
    Args:
        user: L'utilisateur
        size: Taille à afficher ('small', 'medium', 'large')
        css_class: Classes CSS additionnelles
        alt: Texte alternatif
    
    Returns:
        str: HTML sécurisé pour l'affichage
    """
    urls = get_profile_picture_urls(user)
    
    if not alt and user:
        alt = f"Photo de profil de {user.get_full_name()}" if hasattr(user, 'get_full_name') else "Photo de profil"
    
    # S'assurer que la taille demandée existe
    img_url = urls.get(size, urls.get('default'))
    
    # Construire le HTML avec les attributs nécessaires
    html = f'<img src="{img_url}" alt="{alt}" class="profile-picture {size} {css_class}"'
    
    # Ajouter les attributs data pour le chargement progressif
    if not urls.get('legacy') and not urls.get('is_default'):
        for size_name in ('small', 'medium', 'large'):
            if size_name in urls:
                html += f' data-{size_name}="{urls[size_name]}"'
    
    # Ajouter les attributs de performance
    html += ' loading="lazy"'
    
    # Fermer la balise
    html += ' />'
    
    return mark_safe(html)


def invalidate_profile_picture_cache(user_id):
    """
    Invalide le cache des URLs de photo de profil.
    
    Args:
        user_id: L'ID de l'utilisateur
    """
    # Trouver et supprimer toutes les clés correspondantes
    keys_to_delete = []
    
    # Format de clé: profile_pic_urls_{user_id}_*
    prefix = f"profile_pic_urls_{user_id}_"
    
    # Trouver les clés à supprimer
    if hasattr(cache, '_cache'):  # Pour les backends par défaut
        for key in cache._cache.keys():
            if isinstance(key, str) and key.startswith(prefix):
                keys_to_delete.append(key)
    
    # Supprimer les clés
    for key in keys_to_delete:
        cache.delete(key)


# -----------------------------------------------------------------------------
# Main Integration Functions
# -----------------------------------------------------------------------------

def process_uploaded_profile_picture(user, file_data, update_model=True):
    """
    Traite une photo de profil téléchargée et met à jour le modèle utilisateur.
    
    Args:
        user: L'instance User
        file_data: Le fichier téléchargé (InMemoryUploadedFile ou TemporaryUploadedFile)
        update_model: Si True, met à jour le modèle utilisateur
    
    Returns:
        Dict: Informations sur le traitement effectué
    """
    if not user or not file_data:
        return {"success": False, "error": "Utilisateur ou fichier manquant"}
    
    try:
        # Lire les données du fichier
        file_data.seek(0)
        image_data = file_data.read()
        
        # Déterminer le format d'entrée
        ext = os.path.splitext(file_data.name)[1].lower().lstrip('.')
        format_name = SUPPORTED_IMAGE_FORMATS.get(ext, PREFERRED_FORMAT)
        
        # Traiter l'image
        user_id = str(user.id)
        processed = process_profile_picture(image_data, user_id, format_name)
        
        # Sauvegarder les images
        saved_paths = save_processed_images(processed)
        
        # Mettre à jour le modèle si demandé
        if update_model:
            with transaction.atomic():
                user.profile_picture = saved_paths['optimized']
                user.save(update_fields=['profile_picture'])
            
            # Invalider le cache
            invalidate_profile_picture_cache(user.id)
        
        # Nettoyer les anciennes versions
        clean_old_versions(user_id)
        
        return {
            "success": True,
            "paths": saved_paths,
            "metadata": processed['metadata']
        }
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la photo de profil: {e}")
        return {"success": False, "error": str(e)}


def delete_profile_picture(user):
    """
    Supprime la photo de profil d'un utilisateur.
    
    Args:
        user: L'instance User
    
    Returns:
        bool: True si la suppression a réussi
    """
    if not user or not hasattr(user, 'profile_picture') or not user.profile_picture:
        return False
    
    try:
        # Déterminer le format (legacy ou nouveau)
        profile_picture_path = str(user.profile_picture)
        is_legacy = profile_picture_path.startswith(LEGACY_DIR) or LEGACY_DIR in profile_picture_path
        
        # Supprimer les fichiers
        if is_legacy:
            # Supprimer uniquement le fichier legacy
            full_path = os.path.join(settings.MEDIA_ROOT, profile_picture_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        else:
            # Pour le nouveau format, supprimer le répertoire utilisateur complet
            user_id = str(user.id)
            user_dir = os.path.join(settings.MEDIA_ROOT, PROFILES_DIR, user_id)
            
            if os.path.exists(user_dir):
                shutil.rmtree(user_dir)
        
        # Mettre à jour le modèle
        with transaction.atomic():
            user.profile_picture = ''
            user.save(update_fields=['profile_picture'])
        
        # Invalider le cache
        invalidate_profile_picture_cache(user.id)
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la photo de profil: {e}")
        return False