import os
import shutil
import uuid
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image
from io import BytesIO

User = get_user_model()

class Command(BaseCommand):
    """
    Commande pour migrer les photos de profil de l'ancien format au nouveau format.
    
    Cette commande:
    1. Trouve les photos de profil existantes dans l'ancien répertoire
    2. Crée la nouvelle structure de répertoires
    3. Migre chaque photo vers le nouveau format
    4. Met à jour les références dans la base de données
    
    Usage: python manage.py migrate_profile_pictures [--force] [--user-id=123]
    """
    help = 'Migre les photos de profil de l\'ancien format vers le nouveau format'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la migration sans demander de confirmation'
        )
        
        parser.add_argument(
            '--user-id',
            type=int,
            help='Migrer uniquement les photos d\'un utilisateur spécifique'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulation sans effectuer les modifications'
        )
    
    def handle(self, *args, **options):
        force = options['force']
        user_id = options.get('user_id')
        dry_run = options.get('dry_run')
        
        # Vérifier les répertoires source et destination
        old_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pictures')
        new_base_dir = os.path.join(settings.MEDIA_ROOT, 'profiles')
        
        if not os.path.exists(old_dir):
            self.stdout.write(self.style.ERROR(f"Le répertoire source {old_dir} n'existe pas."))
            return
        
        # Créer le répertoire de destination s'il n'existe pas
        if not os.path.exists(new_base_dir) and not dry_run:
            os.makedirs(new_base_dir)
        
        # Confirmation
        if not force and not dry_run:
            confirm = input(f"Migrer les photos de profil de {old_dir} vers {new_base_dir} ? [y/N] ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("Migration annulée."))
                return
        
        # Trouver les utilisateurs à migrer
        if user_id:
            users = User.objects.filter(id=user_id)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"Utilisateur avec ID {user_id} non trouvé."))
                return
        else:
            # Trouver les utilisateurs avec des photos de profil
            users = User.objects.exclude(profile_picture='')
        
        self.stdout.write(f"Migration pour {users.count()} utilisateurs...")
        
        migrated_count = 0
        error_count = 0
        
        # Migrer chaque utilisateur
        for user in users:
            old_path = None
            
            try:
                # Extraire le chemin de la photo actuelle
                profile_picture_path = str(user.profile_picture)
                
                # Vérifier si c'est déjà au nouveau format
                if 'profiles/' in profile_picture_path and '/optimized/' in profile_picture_path:
                    self.stdout.write(f"L'utilisateur {user.id} utilise déjà le nouveau format.")
                    continue
                
                # Extraire le nom de fichier de l'ancien chemin
                if profile_picture_path.startswith('profile_pictures/'):
                    old_filename = profile_picture_path.replace('profile_pictures/', '')
                    old_path = os.path.join(old_dir, old_filename)
                    
                    if not os.path.exists(old_path):
                        self.stdout.write(self.style.WARNING(
                            f"Fichier introuvable pour l'utilisateur {user.id}: {old_path}"
                        ))
                        error_count += 1
                        continue
                    
                    # Créer la structure pour le nouvel utilisateur
                    user_dir = os.path.join(new_base_dir, str(user.id))
                    user_original_dir = os.path.join(user_dir, 'original')
                    user_optimized_dir = os.path.join(user_dir, 'optimized')
                    user_thumbnails_dir = os.path.join(user_dir, 'thumbnails')
                    
                    # Générer les noms de fichiers avec UUID
                    timestamp = int(time.time())
                    unique_id = uuid.uuid4().hex
                    _, ext = os.path.splitext(old_path)
                    ext = ext.lower()  # Normaliser l'extension
                    
                    # Créer les répertoires nécessaires
                    if not dry_run:
                        for directory in [user_dir, user_original_dir, user_optimized_dir, user_thumbnails_dir]:
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                    
                    # Chemins des nouveaux fichiers
                    new_original_path = os.path.join(user_original_dir, f"{timestamp}_{unique_id}{ext}")
                    new_optimized_path = os.path.join(user_optimized_dir, f"{unique_id}{ext}")
                    
                    # Chemins relatifs pour la base de données
                    rel_optimized_path = os.path.join('profiles', str(user.id), 'optimized', f"{unique_id}{ext}")
                    
                    # Lire l'image
                    with Image.open(old_path) as img:
                        # Convertir en RGB si nécessaire
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Copier l'original
                        if not dry_run:
                            shutil.copy2(old_path, new_original_path)
                            
                            # Générer la version optimisée
                            max_size = (800, 800)
                            img.thumbnail(max_size, Image.LANCZOS)
                            img.save(new_optimized_path, format='JPEG', quality=85, optimize=True)
                            
                            # Générer les vignettes
                            for size_name, dimensions in [
                                ('small', (50, 50)),
                                ('medium', (150, 150)),
                                ('large', (300, 300))
                            ]:
                                thumb = img.copy()
                                thumb.thumbnail(dimensions, Image.LANCZOS)
                                thumb_path = os.path.join(user_thumbnails_dir, f"{size_name}_{unique_id}{ext}")
                                thumb.save(thumb_path, format='JPEG', quality=85, optimize=True)
                            
                            # Mettre à jour la référence dans la base de données
                            with transaction.atomic():
                                user.profile_picture = rel_optimized_path
                                user.save(update_fields=['profile_picture'])
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Migration réussie pour l'utilisateur {user.id}: {old_path} → {rel_optimized_path}"
                    ))
                    migrated_count += 1
                
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Format non reconnu pour l'utilisateur {user.id}: {profile_picture_path}"
                    ))
                    error_count += 1
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Erreur lors de la migration pour l'utilisateur {user.id}: {str(e)}"
                ))
                error_count += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"Simulation terminée. {migrated_count} utilisateurs seraient migrés, {error_count} erreurs."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Migration terminée. {migrated_count} utilisateurs migrés, {error_count} erreurs."
            ))