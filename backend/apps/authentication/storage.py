import os
import uuid
import io
import datetime
import logging
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from PIL import Image
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

@deconstructible
class ProfileStorage(FileSystemStorage):
    """
    Storage backend for user profile pictures with social media-like organization.

    Caractéristiques:
    - Organisation par ID utilisateur
    - Génération automatique de plusieurs tailles d'images (petit, moyen, grand)
    - Conservation des versions originales avec historique
    - Optimisation des images pour l'affichage
    - Compatibilité avec l'ancien système de stockage
    """
    
    def __init__(self, **kwargs):
        # Configuration de base
        self.base_dir = 'profiles'
        location = kwargs.pop('location', os.path.join(settings.MEDIA_ROOT, self.base_dir))
        base_url = kwargs.pop('base_url', f'{settings.MEDIA_URL}{self.base_dir}/')
        super().__init__(location=location, base_url=base_url, **kwargs)
        
        # Tailles d'images et qualité
        self.sizes = {
            'small': (50, 50),      # Pour commentaires, notifications
            'medium': (150, 150),   # Pour les cartes profil
            'large': (300, 300),    # Pour la page profil
        }
        self.max_size = (800, 800)  # Taille max pour version optimisée
        self.quality = 85           # Qualité JPEG (1-100)
        
        # Comportement de stockage
        self.keep_originals = True  # Garder les fichiers originaux
        self.max_versions = 5       # Nombre de versions à conserver
    
    def get_available_name(self, name, max_length=None):
        """
        Génère un nom de fichier unique avec UUID et structure par utilisateur
        """
        # Extraire l'ID utilisateur du chemin si présent
        user_id = self._extract_user_id(name)
        
        # Générer un identifiant unique
        unique_id = uuid.uuid4().hex
        timestamp = int(datetime.datetime.now().timestamp())
        
        # Extraire l'extension
        _, ext = os.path.splitext(name)
        ext = ext.lower()
        
        # Créer le chemin approprié selon le type d'image
        if 'original' in name:
            # Originaux stockés avec horodatage pour l'historique
            path = f"{self.base_dir}/{user_id}/original/{timestamp}_{unique_id}{ext}"
        elif any(size in name for size in self.sizes.keys()):
            # Vignettes spécifiques
            for size in self.sizes.keys():
                if size in name:
                    path = f"{self.base_dir}/{user_id}/thumbnails/{size}_{unique_id}{ext}"
                    break
            else:
                path = f"{self.base_dir}/{user_id}/thumbnails/small_{unique_id}{ext}"
        else:
            # Version optimisée par défaut
            path = f"{self.base_dir}/{user_id}/optimized/{unique_id}{ext}"
        
        return super().get_available_name(path, max_length)
    
    def _extract_user_id(self, path):
        """Extraire l'ID utilisateur du chemin, ou utiliser 'temp' par défaut"""
        parts = path.split('/')
        user_id = 'temp'
        
        # Essayer de trouver l'ID utilisateur dans le chemin
        for i, part in enumerate(parts):
            if i > 0 and part.isdigit():
                user_id = part
                break
        
        return user_id
    
    def _save(self, name, content):
        """
        Enregistre le fichier et crée les versions additionnelles pour les images
        """
        # Traiter uniquement les fichiers image
        if self._is_image_file(name):
            try:
                # Extraire l'ID utilisateur
                user_id = self._extract_user_id(name)
                
                # Ouvrir et traiter l'image avec PIL
                img = Image.open(content)
                
                # Convertir en RGB si nécessaire (pour PNG transparents)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Générer un ID unique pour les noms de fichiers
                unique_id = uuid.uuid4().hex
                timestamp = int(datetime.datetime.now().timestamp())
                _, ext = os.path.splitext(name)
                ext = ext.lower()
                
                # Générer les chemins pour toutes les versions
                paths = {
                    'original': f"{self.base_dir}/{user_id}/original/{timestamp}_{unique_id}{ext}",
                    'optimized': f"{self.base_dir}/{user_id}/optimized/{unique_id}{ext}",
                    'thumbnails': {}
                }
                
                for size_name, dimensions in self.sizes.items():
                    paths['thumbnails'][size_name] = f"{self.base_dir}/{user_id}/thumbnails/{size_name}_{unique_id}{ext}"
                
                # Sauvegarder l'original si demandé
                if self.keep_originals:
                    content.seek(0)  # Remettre le pointeur au début
                    super()._save(paths['original'], content)
                    
                    # Nettoyer les versions anciennes si nécessaire
                    self._cleanup_old_versions(user_id)
                
                # Créer et sauvegarder la version optimisée
                optimized = self._resize_image(img, self.max_size)
                optimized_content = self._image_to_content(optimized)
                optimized_path = super()._save(paths['optimized'], optimized_content)
                
                # Créer et sauvegarder les vignettes
                for size_name, dimensions in self.sizes.items():
                    thumb = self._resize_image(img.copy(), dimensions)
                    thumb_content = self._image_to_content(thumb)
                    super()._save(paths['thumbnails'][size_name], thumb_content)
                
                # Retourner le chemin correspondant au type demandé
                if 'original' in name:
                    return paths['original']
                elif any(size in name for size in self.sizes.keys()):
                    for size in self.sizes.keys():
                        if size in name:
                            return paths['thumbnails'][size]
                    return paths['thumbnails']['small']
                else:
                    return paths['optimized']
                
            except Exception as e:
                logger.exception(f"Erreur lors du traitement de l'image: {e}")
                return super()._save(name, content)
        
        # Pour les fichiers non-image
        return super()._save(name, content)
    
    def _is_image_file(self, name):
        """Vérifier si le fichier est une image basée sur l'extension"""
        ext = os.path.splitext(name)[1].lower()
        return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    def _resize_image(self, img, size):
        """Redimensionner une image en conservant les proportions"""
        img.thumbnail(size, Image.LANCZOS)
        return img
    
    def _image_to_content(self, img):
        """Convertir une image PIL en ContentFile Django"""
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG', quality=self.quality, optimize=True)
        return ContentFile(img_io.getvalue())
    
    def _cleanup_old_versions(self, user_id):
        """Supprimer les anciennes versions des photos de profil"""
        if user_id == 'temp':
            return
            
        try:
            original_dir = os.path.join(self.location, user_id, 'original')
            
            if not os.path.exists(original_dir):
                return
                
            files = sorted(os.listdir(original_dir), reverse=True)
            
            # Garder seulement les versions les plus récentes
            for old_file in files[self.max_versions:]:
                try:
                    os.remove(os.path.join(original_dir, old_file))
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du fichier {old_file}: {e}")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage pour l'utilisateur {user_id}: {e}")


# Classe pour la compatibilité avec les migrations existantes
@deconstructible
class SecureUniqueFileStorage(ProfileStorage):
    """
    Alias pour ProfileStorage pour assurer la compatibilité avec les migrations existantes.
    Cette classe est maintenue uniquement pour la compatibilité avec le code existant.
    Utilisez ProfileStorage pour les nouvelles implémentations.
    """
    pass


class CreateProfileDirectories(BaseCommand):
    """
    Commande Django pour créer les répertoires nécessaires pour les photos de profil
    
    Usage: python manage.py create_profile_directories
    """
    help = 'Crée les répertoires nécessaires pour les photos de profil'
    
    def handle(self, *args, **options):
        base_dir = os.path.join(settings.MEDIA_ROOT, 'profiles')
        
        # Créer le répertoire de base
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            self.stdout.write(f"Répertoire créé: {base_dir}")
        
        # Créer un répertoire temporaire pour les fichiers sans utilisateur
        temp_dir = os.path.join(base_dir, 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            self.stdout.write(f"Répertoire créé: {temp_dir}")
            
        # Créer les sous-répertoires pour 'temp'
        for subdir in ['original', 'optimized', 'thumbnails']:
            path = os.path.join(temp_dir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
                self.stdout.write(f"Répertoire créé: {path}")
        
        self.stdout.write(self.style.SUCCESS("Structure de répertoires créée avec succès"))