"""
Service de stockage Supabase pour les photos de profil
"""

import os
import uuid
import logging
from typing import Optional, Dict, Any
from PIL import Image
from io import BytesIO
from django.conf import settings
from supabase import create_client, Client
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    """Service pour gérer le stockage des fichiers dans Supabase Storage"""
    
    def __init__(self):
        try:
            logger.info(f"Initializing Supabase client with URL: {settings.SUPABASE_URL[:30]}...")
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured")
            
            # Utiliser la clé SERVICE_ROLE pour les opérations d'écriture
            self.supabase: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            self.bucket_name = "profile-pictures"
            logger.info("Supabase client initialized successfully with SERVICE_ROLE key")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def upload_profile_picture(self, user_id: str, file, original_filename: str) -> Dict[str, Any]:
        """
        Upload une photo de profil vers Supabase Storage
        
        Args:
            user_id: ID de l'utilisateur
            file: Fichier image à uploader
            original_filename: Nom original du fichier
            
        Returns:
            Dict contenant les URLs et informations du fichier uploadé
        """
        try:
            logger.info(f"Starting upload for user {user_id}, file: {original_filename}")
            
            # Générer un nom de fichier unique
            file_extension = os.path.splitext(original_filename)[1].lower()
            if not file_extension:
                file_extension = '.jpg'
            
            timestamp = str(int(uuid.uuid4().int))[:10]
            filename = f"{user_id}/{timestamp}{file_extension}"
            logger.info(f"Generated filename: {filename}")
            
            # Préparer le fichier pour l'upload
            logger.info("Preparing image for upload...")
            file_data = self._prepare_image_for_upload(file)
            logger.info(f"Image prepared, size: {len(file_data)} bytes")
            
            # Vérifier que le bucket existe, sinon essayer de le créer
            self._ensure_bucket_exists()
            
            # Upload vers Supabase Storage
            logger.info(f"Uploading to bucket: {self.bucket_name}")
            response = self.supabase.storage.from_(self.bucket_name).upload(
                filename,
                file_data,
                file_options={
                    'content-type': 'image/jpeg',
                    'cache-control': '3600',
                    'upsert': 'false'
                }
            )
            logger.info(f"Upload response: {response}")
            
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Erreur upload Supabase: {response.error}")
                return {
                    'success': False,
                    'error': f"Erreur upload: {response.error}"
                }
            
            # Générer l'URL publique
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(filename)
            logger.info(f"Generated public URL: {public_url}")
            
            # Pour l'instant, ne créer que l'URL originale
            # TODO: Ajouter les variants plus tard si nécessaire
            urls = {'original': public_url}
            
            return {
                'success': True,
                'filename': filename,
                'urls': urls,
                'public_url': public_url
            }
            
        except Exception as e:
            logger.exception(f"Erreur lors de l'upload de la photo de profil: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _ensure_bucket_exists(self):
        """Vérifie que le bucket existe et le crée si nécessaire"""
        try:
            # Essayer de lister les buckets pour vérifier l'existence
            buckets = self.supabase.storage.list_buckets()
            logger.info(f"Available buckets: {[b.name for b in buckets]}")
            
            bucket_exists = any(bucket.name == self.bucket_name for bucket in buckets)
            
            if not bucket_exists:
                logger.warning(f"Bucket {self.bucket_name} does not exist. Creating it...")
                # Créer le bucket avec des permissions publiques pour les lectures
                result = self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={'public': True}
                )
                logger.info(f"Bucket creation result: {result}")
            else:
                logger.info(f"Bucket {self.bucket_name} exists")
                
        except Exception as e:
            logger.error(f"Error checking/creating bucket: {str(e)}")
            # Ne pas lever l'erreur, laisser l'upload essayer
    
    def _prepare_image_for_upload(self, file) -> bytes:
        """Prépare et optimise l'image pour l'upload"""
        try:
            # Ouvrir l'image avec PIL
            if hasattr(file, 'read'):
                image_data = file.read()
                file.seek(0)  # Reset pour d'autres utilisations
            else:
                image_data = file
            
            image = Image.open(BytesIO(image_data))
            
            # Convertir en RGB si nécessaire
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Redimensionner si trop grande
            max_size = getattr(settings, 'PROFILE_PICTURE_MAX_DISPLAY_SIZE', (800, 800))
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Sauvegarder en JPEG optimisé
            output = BytesIO()
            quality = getattr(settings, 'PROFILE_PICTURE_QUALITY', 85)
            image.save(output, format='JPEG', quality=quality, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation de l'image: {str(e)}")
            # En cas d'erreur, retourner les données originales
            if hasattr(file, 'read'):
                file.seek(0)
                return file.read()
            return file
    
    def _create_image_variants(self, user_id: str, image_data: bytes, timestamp: str) -> Dict[str, str]:
        """Crée différentes tailles d'images et les upload"""
        urls = {}
        sizes = getattr(settings, 'PROFILE_PICTURE_SIZES', {
            'small': (50, 50),
            'medium': (150, 150),
            'large': (300, 300)
        })
        
        try:
            original_image = Image.open(BytesIO(image_data))
            
            for size_name, (width, height) in sizes.items():
                # Créer une copie redimensionnée
                resized_image = original_image.copy()
                resized_image.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                # Sauvegarder
                output = BytesIO()
                resized_image.save(output, format='JPEG', quality=85, optimize=True)
                resized_data = output.getvalue()
                
                # Upload vers Supabase
                variant_filename = f"{user_id}/{size_name}_{timestamp}.jpg"
                try:
                    response = self.supabase.storage.from_(self.bucket_name).upload(
                        variant_filename,
                        resized_data,
                        file_options={
                            'content-type': 'image/jpeg',
                            'cache-control': '3600',
                            'upsert': 'false'
                        }
                    )
                    
                    if not (hasattr(response, 'error') and response.error):
                        urls[size_name] = self.supabase.storage.from_(self.bucket_name).get_public_url(variant_filename)
                        
                except Exception as e:
                    logger.warning(f"Impossible de créer la variante {size_name}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Erreur lors de la création des variantes: {str(e)}")
        
        return urls
    
    def delete_profile_picture(self, filename: str) -> bool:
        """Supprime une photo de profil de Supabase Storage"""
        try:
            response = self.supabase.storage.from_(self.bucket_name).remove([filename])
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Erreur suppression Supabase: {response.error}")
                return False
                
            return True
            
        except Exception as e:
            logger.exception(f"Erreur lors de la suppression: {str(e)}")
            return False
    
    def delete_user_profile_pictures(self, user_id: str) -> bool:
        """Supprime toutes les photos de profil d'un utilisateur"""
        try:
            # Lister tous les fichiers de l'utilisateur
            response = self.supabase.storage.from_(self.bucket_name).list(user_id)
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Erreur listage Supabase: {response.error}")
                return False
            
            # Supprimer tous les fichiers
            if response and len(response) > 0:
                files_to_delete = [f"{user_id}/{file['name']}" for file in response]
                delete_response = self.supabase.storage.from_(self.bucket_name).remove(files_to_delete)
                
                if hasattr(delete_response, 'error') and delete_response.error:
                    logger.error(f"Erreur suppression batch Supabase: {delete_response.error}")
                    return False
            
            return True
            
        except Exception as e:
            logger.exception(f"Erreur lors de la suppression des photos utilisateur: {str(e)}")
            return False
    
    def get_profile_picture_url(self, filename: str) -> Optional[str]:
        """Récupère l'URL publique d'une photo de profil"""
        try:
            return self.supabase.storage.from_(self.bucket_name).get_public_url(filename)
        except Exception as e:
            logger.error(f"Erreur récupération URL: {str(e)}")
            return None


# Instance globale du service
supabase_storage = SupabaseStorageService()