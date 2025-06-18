import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
import datetime
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Creates directories for profile pictures and performs maintenance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--rebuild',
            action='store_true',
            dest='rebuild',
            help='Rebuild all thumbnails and optimize existing profile pictures',
        )
        parser.add_argument(
            '--migrate',
            action='store_true',
            dest='migrate',
            help='Migrate from old storage format to new format',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            dest='cleanup',
            help='Clean up old versions of profile pictures',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Force operations without confirmation',
        )

    def handle(self, *args, **options):
        # Create directory structure
        self._create_directory_structure()
        
        if options['migrate']:
            # Migrate from old format to new format
            self._migrate_from_old_format(force=options['force'])
            
        if options['rebuild']:
            # Rebuild thumbnails and optimized versions
            self._rebuild_thumbnails(force=options['force'])
            
        if options['cleanup']:
            # Clean up old versions
            self._cleanup_old_versions(force=options['force'])
            
        self.stdout.write(self.style.SUCCESS('Profile picture maintenance completed'))
    
    def _create_directory_structure(self):
        """Create the required directory structure for profile pictures"""
        # Base directories
        dirs_to_create = [
            settings.PROFILE_PICTURES_ROOT,
            settings.PROFILE_AVATARS_DIR,
            settings.PROFILE_COVERS_DIR,
            
            # Avatar subdirectories
            os.path.join(settings.PROFILE_AVATARS_DIR, 'original'),
            os.path.join(settings.PROFILE_AVATARS_DIR, 'optimized'),
            os.path.join(settings.PROFILE_AVATARS_DIR, 'thumbnails'),
            
            # Cover subdirectories
            os.path.join(settings.PROFILE_COVERS_DIR, 'original'),
            os.path.join(settings.PROFILE_COVERS_DIR, 'optimized'),
        ]
        
        # Create each directory if it doesn't exist
        for directory in dirs_to_create:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.stdout.write(f"Created directory: {directory}")
            else:
                self.stdout.write(f"Directory already exists: {directory}")
                
        # Create a temp directory in each location
        temp_dirs = [
            os.path.join(settings.PROFILE_AVATARS_DIR, 'original', 'temp'),
            os.path.join(settings.PROFILE_AVATARS_DIR, 'optimized', 'temp'),
            os.path.join(settings.PROFILE_AVATARS_DIR, 'thumbnails', 'temp'),
            os.path.join(settings.PROFILE_COVERS_DIR, 'original', 'temp'),
            os.path.join(settings.PROFILE_COVERS_DIR, 'optimized', 'temp'),
        ]
        
        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
    
    def _migrate_from_old_format(self, force=False):
        """Migrate profile pictures from old format to new format"""
        if not force:
            confirm = input("This will migrate profile pictures to the new format. Continue? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Migration cancelled'))
                return
        
        # Get all users with profile pictures
        users_with_pictures = User.objects.filter(~Q(profile_picture=''))
        
        self.stdout.write(f"Found {users_with_pictures.count()} users with profile pictures")
        
        # Old profile pictures directory
        old_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pictures')
        
        # Check if it exists
        if not os.path.exists(old_dir):
            self.stdout.write(self.style.WARNING(f"Old profile pictures directory not found: {old_dir}"))
            return
        
        # Process each user
        for user in users_with_pictures:
            old_path = os.path.join(settings.MEDIA_ROOT, str(user.profile_picture))
            
            if not os.path.exists(old_path):
                self.stdout.write(self.style.WARNING(f"Profile picture not found for user {user.id}: {old_path}"))
                continue
                
            # Create user directories if they don't exist
            user_dirs = [
                os.path.join(settings.PROFILE_AVATARS_DIR, 'original', str(user.id)),
                os.path.join(settings.PROFILE_AVATARS_DIR, 'optimized', str(user.id)),
                os.path.join(settings.PROFILE_AVATARS_DIR, 'thumbnails', str(user.id)),
            ]
            
            for directory in user_dirs:
                if not os.path.exists(directory):
                    os.makedirs(directory)
            
            # Generate a timestamp and UUID for the file
            timestamp = int(datetime.datetime.now().timestamp())
            import uuid
            unique_id = uuid.uuid4().hex
            
            # Get file extension
            _, ext = os.path.splitext(old_path)
            
            # New paths for this file
            new_original_path = os.path.join(
                settings.PROFILE_AVATARS_DIR, 
                'original', 
                str(user.id), 
                f"{timestamp}_{unique_id}{ext}"
            )
            
            # Copy the file to the new location
            try:
                shutil.copy2(old_path, new_original_path)
                self.stdout.write(f"Migrated profile picture for user {user.id}")
                
                # Update the user's profile picture field to point to the new location
                # This will trigger the storage backend to create optimized versions and thumbnails
                from django.core.files.base import File
                with open(new_original_path, 'rb') as f:
                    user.profile_picture.save(
                        os.path.join('profiles/avatars/optimized', str(user.id), f"{unique_id}{ext}"),
                        File(f),
                        save=True
                    )
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error migrating profile picture for user {user.id}: {str(e)}"))
    
    def _rebuild_thumbnails(self, force=False):
        """Rebuild thumbnails and optimized versions for all profile pictures"""
        if not force:
            confirm = input("This will rebuild all thumbnails and optimized versions. Continue? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Rebuild cancelled'))
                return
        
        # Get all users with profile pictures
        users_with_pictures = User.objects.filter(~Q(profile_picture=''))
        
        self.stdout.write(f"Found {users_with_pictures.count()} users with profile pictures")
        
        # Process each user
        for user in users_with_pictures:
            try:
                # Simply saving the model will trigger the storage backend to recreate thumbnails
                # if we first clear the optimized and thumbnails directories
                user_optimized_dir = os.path.join(settings.PROFILE_AVATARS_DIR, 'optimized', str(user.id))
                user_thumbnails_dir = os.path.join(settings.PROFILE_AVATARS_DIR, 'thumbnails', str(user.id))
                
                # Clear the directories
                if os.path.exists(user_optimized_dir):
                    for file in os.listdir(user_optimized_dir):
                        os.remove(os.path.join(user_optimized_dir, file))
                
                if os.path.exists(user_thumbnails_dir):
                    for file in os.listdir(user_thumbnails_dir):
                        os.remove(os.path.join(user_thumbnails_dir, file))
                
                # Get the most recent original file
                user_original_dir = os.path.join(settings.PROFILE_AVATARS_DIR, 'original', str(user.id))
                if os.path.exists(user_original_dir):
                    original_files = os.listdir(user_original_dir)
                    original_files.sort(reverse=True)  # Sort by name (timestamp_uuid.ext)
                    
                    if original_files:
                        original_file = os.path.join(user_original_dir, original_files[0])
                        
                        # Update the user's profile picture field to trigger thumbnail generation
                        from django.core.files.base import File
                        with open(original_file, 'rb') as f:
                            # Extract the UUID from the filename (timestamp_uuid.ext)
                            import os
                            filename = os.path.basename(original_file)
                            parts = filename.split('_', 1)
                            if len(parts) > 1:
                                uuid_ext = parts[1]  # uuid.ext
                                _, ext = os.path.splitext(uuid_ext)
                                
                                # Save with the correct path format
                                user.profile_picture.save(
                                    os.path.join('profiles/avatars/optimized', str(user.id), uuid_ext),
                                    File(f),
                                    save=True
                                )
                                
                                self.stdout.write(f"Rebuilt thumbnails for user {user.id}")
                            else:
                                self.stdout.write(self.style.WARNING(f"Invalid filename format for user {user.id}: {filename}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"No original files found for user {user.id}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Original directory not found for user {user.id}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error rebuilding thumbnails for user {user.id}: {str(e)}"))
    
    def _cleanup_old_versions(self, force=False):
        """Clean up old versions of profile pictures"""
        if not force:
            confirm = input("This will remove old versions of profile pictures. Continue? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Cleanup cancelled'))
                return
        
        # Get maximum versions to keep
        max_versions = getattr(settings, 'PROFILE_PICTURE_MAX_VERSIONS', 5)
        
        # Get all users with profile pictures
        users_with_pictures = User.objects.filter(~Q(profile_picture=''))
        
        self.stdout.write(f"Found {users_with_pictures.count()} users with profile pictures")
        
        # Process each user
        for user in users_with_pictures:
            user_original_dir = os.path.join(settings.PROFILE_AVATARS_DIR, 'original', str(user.id))
            
            if not os.path.exists(user_original_dir):
                continue
                
            # Get all files in the original directory
            original_files = os.listdir(user_original_dir)
            
            # Sort by timestamp (newest first)
            original_files.sort(reverse=True)
            
            # Keep only the specified number of most recent files
            files_to_delete = original_files[max_versions:]
            
            # Delete the older files
            for filename in files_to_delete:
                try:
                    file_path = os.path.join(user_original_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self.stdout.write(f"Deleted old profile picture for user {user.id}: {filename}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to delete {filename} for user {user.id}: {str(e)}"))
            
            self.stdout.write(f"Cleaned up {len(files_to_delete)} old profile pictures for user {user.id}")