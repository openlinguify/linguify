import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO
import json

from django.test import TestCase, override_settings, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError

from ..profile import (
    process_profile_picture,
    ensure_profile_directories,
    save_processed_images,
    clean_old_versions,
    get_profile_picture_urls,
    process_uploaded_profile_picture,
    delete_profile_picture,
)
from ..supabase_storage import SupabaseStorageService

User = get_user_model()

# Créer un répertoire temporaire pour les tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# Image test PNG 1x1 pixel
PNG_1PX = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
    b'\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05'
    b'\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)

# Image test JPG 1x1 pixel
JPG_1PX = (
    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C'
    b'\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b'
    b'\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7)'
    b',,01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c'
    b'!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08'
    b'\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00'
    b'\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01'
    b'\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03'
    b'\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05'
    b'\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82'
    b'\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83'
    b'\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4'
    b'\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5'
    b'\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5'
    b'\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f'
    b'\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01'
    b'\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04'
    b'\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06'
    b'\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4'
    b'\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82'
    b'\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3'
    b'\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4'
    b'\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5'
    b'\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03'
    b'\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00\xff\xd9'
)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProfilePictureTestCase(TestCase):
    """Tests pour le module de gestion des photos de profil."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Créer des dossiers pour les tests
        os.makedirs(os.path.join(TEMP_MEDIA_ROOT, 'profiles'), exist_ok=True)
        os.makedirs(os.path.join(TEMP_MEDIA_ROOT, 'profile_pictures'), exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        # Supprimer les dossiers de test
        shutil.rmtree(TEMP_MEDIA_ROOT)
        super().tearDownClass()
    
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
    
    def test_process_profile_picture_png(self):
        """Test du traitement d'une image PNG."""
        result = process_profile_picture(PNG_1PX, self.user.id, 'PNG')
        
        # Vérifier les métadonnées
        self.assertEqual(result['metadata']['user_id'], self.user.id)
        self.assertEqual(result['metadata']['format'], 'PNG')
        
        # Vérifier les images générées
        self.assertIn('original', result['images'])
        self.assertIn('optimized', result['images'])
        self.assertIn('small', result['images'])
        self.assertIn('medium', result['images'])
        self.assertIn('large', result['images'])
    
    def test_process_profile_picture_jpg(self):
        """Test du traitement d'une image JPG."""
        result = process_profile_picture(JPG_1PX, self.user.id, 'JPEG')
        
        # Vérifier les chemins générés
        self.assertTrue(result['images']['optimized']['path'].startswith(f"profiles/{self.user.id}/optimized/"))
        self.assertTrue(result['images']['original']['path'].startswith(f"profiles/{self.user.id}/original/"))
        
        # Vérifier les formats
        for image_type in ['small', 'medium', 'large']:
            self.assertTrue(result['images'][image_type]['path'].startswith(f"profiles/{self.user.id}/thumbnails/{image_type}_"))
    
    def test_ensure_profile_directories(self):
        """Test de la création des répertoires de profil."""
        paths = ensure_profile_directories(self.user.id)
        
        # Vérifier que les répertoires ont été créés
        for path_type, path in paths.items():
            self.assertTrue(os.path.exists(path))
    
    @patch('os.makedirs')
    def test_ensure_profile_directories_error_handling(self, mock_makedirs):
        """Test de la gestion des erreurs lors de la création des répertoires."""
        mock_makedirs.side_effect = OSError("Permission denied")
        
        # L'erreur ne devrait pas être propagée
        with self.assertLogs(level='ERROR'):
            ensure_profile_directories(self.user.id)
    
    def test_save_processed_images(self):
        """Test de l'enregistrement des images traitées."""
        # Créer des données de test
        result = process_profile_picture(PNG_1PX, self.user.id, 'PNG')
        
        # Sauvegarder les images
        saved_paths = save_processed_images(result)
        
        # Vérifier que les fichiers ont été créés
        for image_type, path in saved_paths.items():
            full_path = os.path.join(TEMP_MEDIA_ROOT, path)
            self.assertTrue(os.path.exists(full_path))
    
    def test_clean_old_versions(self):
        """Test du nettoyage des anciennes versions."""
        # Créer plusieurs versions
        ensure_profile_directories(self.user.id)
        original_dir = os.path.join(TEMP_MEDIA_ROOT, 'profiles', str(self.user.id), 'original')
        
        # Créer 10 fichiers test
        for i in range(10):
            with open(os.path.join(original_dir, f"{i}_test.jpg"), 'wb') as f:
                f.write(JPG_1PX)
        
        # Nettoyer en gardant seulement 3 versions
        deleted = clean_old_versions(self.user.id, max_versions=3)
        
        # Vérifier que 7 fichiers ont été supprimés
        self.assertEqual(deleted, 7)
        
        # Vérifier qu'il reste 3 fichiers
        remaining = os.listdir(original_dir)
        self.assertEqual(len(remaining), 3)
    
    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    def test_get_profile_picture_urls_default(self, mock_cache_set, mock_cache_get):
        """Test de l'obtention des URLs par défaut."""
        mock_cache_get.return_value = None
        
        # Utilisateur sans photo
        self.user.profile_picture = ''
        self.user.save()
        
        result = get_profile_picture_urls(self.user)
        
        # Vérifier le format du résultat
        self.assertIn('is_default', result)
        self.assertTrue(result['is_default'])
        
        # Vérifier les URLs par défaut
        for size in ['small', 'medium', 'large', 'optimized']:
            self.assertIn(size, result)
            self.assertTrue(result[size].startswith('/static/'))
    
    def test_get_profile_picture_urls_legacy(self):
        """Test de l'obtention des URLs pour un format legacy."""
        # Simuler une photo au format legacy
        legacy_path = 'profile_pictures/test.jpg'
        
        # Créer le fichier
        os.makedirs(os.path.dirname(os.path.join(TEMP_MEDIA_ROOT, legacy_path)), exist_ok=True)
        with open(os.path.join(TEMP_MEDIA_ROOT, legacy_path), 'wb') as f:
            f.write(JPG_1PX)
            
        # Mettre à jour l'utilisateur
        self.user.profile_picture = legacy_path
        self.user.save()
        
        # Obtenir les URLs
        with patch('django.core.files.storage.default_storage.url', return_value='/media/profile_pictures/test.jpg'):
            result = get_profile_picture_urls(self.user, use_cache=False)
        
        # Vérifier que c'est bien détecté comme legacy
        self.assertIn('legacy', result)
        self.assertTrue(result['legacy'])
        
        # Vérifier que toutes les URLs pointent vers la même image
        self.assertEqual(result['small'], result['medium'])
        self.assertEqual(result['medium'], result['large'])
        self.assertEqual(result['large'], result['optimized'])
        self.assertEqual(result['optimized'], result['default'])
    
    def test_process_uploaded_profile_picture(self):
        """Test du traitement d'une photo téléchargée."""
        # Créer un faux fichier téléchargé
        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Traiter la photo
        result = process_uploaded_profile_picture(self.user, uploaded_file)
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertIn('paths', result)
        self.assertIn('metadata', result)
        
        # Vérifier que le modèle a été mis à jour
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.profile_picture, '')
        
        # Vérifier que le fichier existe
        self.assertTrue(os.path.exists(os.path.join(
            TEMP_MEDIA_ROOT, 
            result['paths']['optimized']
        )))
    
    def test_delete_profile_picture(self):
        """Test de la suppression d'une photo de profil."""
        # Créer une photo
        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Traiter la photo
        process_uploaded_profile_picture(self.user, uploaded_file)
        
        # Supprimer la photo
        result = delete_profile_picture(self.user)
        
        # Vérifier le résultat
        self.assertTrue(result)
        
        # Vérifier que le modèle a été mis à jour
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_picture, '')
        
        # Vérifier que les fichiers ont été supprimés
        user_dir = os.path.join(TEMP_MEDIA_ROOT, 'profiles', str(self.user.id))
        self.assertFalse(os.path.exists(user_dir))
    
    def test_integrate_with_model(self):
        """Test d'intégration complet avec le modèle utilisateur."""
        # Créer une photo
        uploaded_file = SimpleUploadedFile(
            name='test.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Traiter la photo
        process_uploaded_profile_picture(self.user, uploaded_file)
        
        # Vérifier que la photo est accessible
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.profile_picture, '')
        
        # Obtenir les URLs
        with patch('django.core.files.storage.default_storage.url', 
                  return_value=f'/media/profiles/{self.user.id}/optimized/test.jpg'):
            urls = get_profile_picture_urls(self.user, use_cache=False)
        
        # Vérifier les URLs
        self.assertIn('optimized', urls)
        self.assertIn('small', urls)
        self.assertIn('medium', urls)
        self.assertIn('large', urls)
        
        # Supprimer la photo
        delete_profile_picture(self.user)
        
        # Vérifier que la photo a été supprimée
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_picture, '')


class SupabaseProfilePictureTestCase(TestCase):
    """Tests pour l'upload de photos de profil avec Supabase."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.client = Client()
        self.client.login(username="testuser", password="password123")
    
    @patch('apps.authentication.supabase_storage.SupabaseStorageService.upload_profile_picture')
    def test_supabase_upload_success(self, mock_upload):
        """Test de l'upload réussi vers Supabase."""
        # Mock successful upload
        mock_upload.return_value = {
            'success': True,
            'public_url': 'https://supabase.example.com/storage/v1/object/public/profiles/123/profile.jpg',
            'filename': 'profile_123.jpg',
            'path': 'profiles/123/profile_123.jpg'
        }
        
        # Créer un fichier test
        profile_pic = SimpleUploadedFile(
            name='test.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Faire la requête POST
        response = self.client.post(
            reverse('settings'),
            {
                'setting_type': 'profile',
                'profile_picture': profile_pic,
                'username': self.user.username,
                'email': self.user.email
            },
            format='multipart'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('profile_picture_url', data)
        
        # Vérifier que l'utilisateur a été mis à jour
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile_picture_url, 'https://supabase.example.com/storage/v1/object/public/profiles/123/profile.jpg')
        self.assertEqual(self.user.profile_picture_filename, 'profile_123.jpg')
        self.assertIsNone(self.user.profile_picture.name if self.user.profile_picture else None)
    
    @patch('apps.authentication.supabase_storage.SupabaseStorageService.upload_profile_picture')
    def test_supabase_upload_failure(self, mock_upload):
        """Test de l'échec de l'upload vers Supabase."""
        # Mock failed upload
        mock_upload.return_value = {
            'success': False,
            'error': 'Network error'
        }
        
        # Créer un fichier test
        profile_pic = SimpleUploadedFile(
            name='test.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Faire la requête POST
        response = self.client.post(
            reverse('settings'),
            {
                'setting_type': 'profile',
                'profile_picture': profile_pic,
                'username': self.user.username,
                'email': self.user.email
            },
            format='multipart'
        )
        
        # Vérifier la réponse d'erreur
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Network error', data['message'])
        
        # Vérifier que l'utilisateur n'a pas été mis à jour
        self.user.refresh_from_db()
        self.assertIsNone(self.user.profile_picture_url)
    
    @patch('apps.authentication.supabase_storage.SupabaseStorageService')
    def test_supabase_storage_service_integration(self, mock_storage_class):
        """Test de l'intégration complète avec SupabaseStorageService."""
        # Mock instance
        mock_instance = MagicMock()
        mock_storage_class.return_value = mock_instance
        
        # Mock upload method
        mock_instance.upload_profile_picture.return_value = {
            'success': True,
            'public_url': 'https://supabase.example.com/storage/v1/object/public/profiles/user123/avatar.jpg',
            'filename': 'avatar_123.jpg',
            'path': 'profiles/user123/avatar_123.jpg'
        }
        
        # Créer un fichier test
        profile_pic = SimpleUploadedFile(
            name='avatar.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Importer et utiliser le service
        from apps.authentication.utils.supabase_storage import SupabaseStorageService
        service = SupabaseStorageService()
        result = service.upload_profile_picture(
            user_id=str(self.user.id),
            file=profile_pic,
            original_filename='avatar.jpg'
        )
        
        # Vérifier l'appel
        mock_instance.upload_profile_picture.assert_called_once_with(
            user_id=str(self.user.id),
            file=profile_pic,
            original_filename='avatar.jpg'
        )
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertIn('public_url', result)
    
    def test_profile_picture_display_after_upload(self):
        """Test que la photo de profil s'affiche correctement après upload."""
        # Définir une URL Supabase sur l'utilisateur
        self.user.profile_picture_url = 'https://supabase.example.com/storage/v1/object/public/profiles/123/photo.jpg'
        self.user.save()
        
        # Vérifier que get_profile_picture_url retourne l'URL Supabase
        self.assertEqual(
            self.user.get_profile_picture_url,
            'https://supabase.example.com/storage/v1/object/public/profiles/123/photo.jpg'
        )
    
    @patch('apps.authentication.supabase_storage.SupabaseStorageService.upload_profile_picture')
    def test_ajax_response_includes_updated_url(self, mock_upload):
        """Test que la réponse AJAX inclut l'URL mise à jour."""
        # Mock successful upload
        mock_upload.return_value = {
            'success': True,
            'public_url': 'https://supabase.example.com/storage/v1/object/public/profiles/999/new.jpg',
            'filename': 'new_999.jpg'
        }
        
        # Créer un fichier test
        profile_pic = SimpleUploadedFile(
            name='new.jpg',
            content=JPG_1PX,
            content_type='image/jpeg'
        )
        
        # Faire la requête AJAX
        response = self.client.post(
            reverse('settings'),
            {
                'setting_type': 'profile',
                'profile_picture': profile_pic,
                'username': self.user.username,
                'email': self.user.email
            },
            format='multipart',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['profile_picture_url'], 'https://supabase.example.com/storage/v1/object/public/profiles/999/new.jpg')
    
    def test_profile_picture_validation(self):
        """Test de la validation des fichiers uploadés."""
        # Fichier trop grand (simulé)
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        large_file = SimpleUploadedFile(
            name='large.jpg',
            content=large_content,
            content_type='image/jpeg'
        )
        
        # La validation devrait se faire côté modèle/formulaire
        # Pour ce test, on vérifie juste que le fichier est rejeté
        with self.assertRaises(ValidationError):
            from apps.authentication.models import validate_profile_picture
            validate_profile_picture(large_file)