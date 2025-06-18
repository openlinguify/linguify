"""
Service de stockage Supabase pour les CVs et documents d'application
"""

import os
import uuid
import logging
from typing import Optional, Dict, Any
from django.conf import settings
from supabase import create_client, Client
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)

class JobsSupabaseStorageService:
    """Service pour gérer le stockage des CVs dans Supabase Storage"""
    
    def __init__(self):
        try:
            logger.info(f"Initializing Supabase client for jobs storage...")
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured")
            
            # Utiliser la clé SERVICE_ROLE pour les opérations d'écriture
            self.supabase: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            self.bucket_name = "job-applications"
            logger.info("Jobs Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Jobs Supabase client: {str(e)}")
            raise
    
    def upload_resume(self, application_id: str, file, original_filename: str) -> Dict[str, Any]:
        """
        Upload un CV vers Supabase Storage
        
        Args:
            application_id: ID de l'application
            file: Fichier CV à uploader
            original_filename: Nom original du fichier
            
        Returns:
            Dict contenant les URLs et informations du fichier uploadé
        """
        try:
            logger.info(f"Starting resume upload for application {application_id}, file: {original_filename}")
            
            # Générer un nom de fichier unique
            file_extension = os.path.splitext(original_filename)[1].lower()
            if not file_extension:
                file_extension = '.pdf'
            
            timestamp = str(int(uuid.uuid4().int))[:10]
            filename = f"resumes/{application_id}/{timestamp}_{original_filename}"
            logger.info(f"Generated filename: {filename}")
            
            # Préparer le fichier pour l'upload
            file_data = self._prepare_file_for_upload(file)
            logger.info(f"File prepared, size: {len(file_data)} bytes")
            
            # Vérifier que le bucket existe, sinon essayer de le créer
            self._ensure_bucket_exists()
            
            # Déterminer le content-type
            content_type = self._get_content_type(file_extension)
            
            # Upload vers Supabase Storage
            logger.info(f"Uploading to bucket: {self.bucket_name}")
            response = self.supabase.storage.from_(self.bucket_name).upload(
                filename,
                file_data,
                file_options={
                    'content-type': content_type,
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
            
            # Générer l'URL publique (accessible uniquement avec authentification)
            # Note: Pour les CVs, on ne génère PAS d'URL publique pour la sécurité
            # On stocke seulement le chemin du fichier
            
            return {
                'success': True,
                'filename': filename,
                'original_filename': original_filename,
                'file_path': filename,
                'content_type': content_type
            }
            
        except Exception as e:
            logger.exception(f"Erreur lors de l'upload du CV: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_resume_download_url(self, filename: str, expires_in: int = 3600) -> Optional[str]:
        """
        Génère une URL de téléchargement sécurisée temporaire pour un CV
        
        Args:
            filename: Nom du fichier dans Supabase
            expires_in: Durée de validité en secondes (défaut: 1 heure)
            
        Returns:
            URL de téléchargement temporaire ou None si erreur
        """
        try:
            # Créer une URL signée temporaire
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                filename,
                expires_in
            )
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Erreur génération URL signée: {response.error}")
                return None
            
            return response.get('signedURL')
            
        except Exception as e:
            logger.error(f"Erreur génération URL de téléchargement: {str(e)}")
            return None
    
    def _ensure_bucket_exists(self):
        """Vérifie que le bucket existe et le crée si nécessaire"""
        try:
            # Essayer de lister les buckets pour vérifier l'existence
            buckets = self.supabase.storage.list_buckets()
            logger.info(f"Available buckets: {[b.name for b in buckets]}")
            
            bucket_exists = any(bucket.name == self.bucket_name for bucket in buckets)
            
            if not bucket_exists:
                logger.warning(f"Bucket {self.bucket_name} does not exist. Creating it...")
                # Créer le bucket PRIVÉ pour les CVs (sécurité)
                result = self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={'public': False}  # Bucket privé pour la sécurité
                )
                logger.info(f"Bucket creation result: {result}")
            else:
                logger.info(f"Bucket {self.bucket_name} exists")
                
        except Exception as e:
            logger.error(f"Error checking/creating bucket: {str(e)}")
    
    def _prepare_file_for_upload(self, file) -> bytes:
        """Prépare le fichier pour l'upload"""
        try:
            if hasattr(file, 'read'):
                file_data = file.read()
                file.seek(0)  # Reset pour d'autres utilisations
                return file_data
            else:
                return file
                
        except Exception as e:
            logger.error(f"Erreur lors de la préparation du fichier: {str(e)}")
            raise
    
    def _get_content_type(self, file_extension: str) -> str:
        """Détermine le content-type basé sur l'extension"""
        content_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    def delete_resume(self, filename: str) -> bool:
        """Supprime un CV de Supabase Storage"""
        try:
            response = self.supabase.storage.from_(self.bucket_name).remove([filename])
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Erreur suppression Supabase: {response.error}")
                return False
                
            return True
            
        except Exception as e:
            logger.exception(f"Erreur lors de la suppression: {str(e)}")
            return False
    
    def delete_application_files(self, application_id: str) -> bool:
        """Supprime tous les fichiers d'une application"""
        try:
            # Lister tous les fichiers de l'application
            folder_path = f"resumes/{application_id}"
            response = self.supabase.storage.from_(self.bucket_name).list(folder_path)
            
            if hasattr(response, 'error') and response.error:
                logger.error(f"Erreur listage Supabase: {response.error}")
                return False
            
            # Supprimer tous les fichiers
            if response and len(response) > 0:
                files_to_delete = [f"{folder_path}/{file['name']}" for file in response]
                delete_response = self.supabase.storage.from_(self.bucket_name).remove(files_to_delete)
                
                if hasattr(delete_response, 'error') and delete_response.error:
                    logger.error(f"Erreur suppression batch Supabase: {delete_response.error}")
                    return False
            
            return True
            
        except Exception as e:
            logger.exception(f"Erreur lors de la suppression des fichiers application: {str(e)}")
            return False


# Instance globale du service
jobs_supabase_storage = JobsSupabaseStorageService()