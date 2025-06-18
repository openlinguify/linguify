import os
import uuid
import io
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from PIL import Image
from django.core.files.base import ContentFile
import datetime
import logging

logger = logging.getLogger(__name__)

@deconstructible
class ProfilePhotoStorage(FileSystemStorage):
    """
    Advanced storage backend for user profile pictures with social media-like organization.
    
    Features:
    - Organizes files by user ID for better isolation
    - Creates multiple thumbnail sizes automatically
    - Preserves original uploads with timestamp versioning
    - Optimizes images for web display
    - Compatible with CDN deployments
    """
    
    def __init__(self, **kwargs):
        # Base directory structure
        self.base_dir = 'profiles/avatars'
        
        # Set default storage location
        location = kwargs.pop('location', os.path.join(settings.MEDIA_ROOT, self.base_dir))
        base_url = kwargs.pop('base_url', f'{settings.MEDIA_URL}{self.base_dir}/')
        super().__init__(location=location, base_url=base_url, **kwargs)
        
        # Define sizes based on settings or defaults
        self.sizes = getattr(settings, 'PROFILE_PICTURE_SIZES', {
            'small': (50, 50),      # For comments, notifications
            'medium': (150, 150),   # For profile cards in listings
            'large': (300, 300),    # For profile pages
        })
        
        # Size limits for original images
        self.max_size = getattr(settings, 'PROFILE_PICTURE_MAX_DISPLAY_SIZE', (800, 800))
        
        # Image quality (1-100 for JPEG)
        self.image_quality = getattr(settings, 'PROFILE_PICTURE_QUALITY', 85)
        
        # Setting to determine if we keep original files
        self.keep_originals = getattr(settings, 'PROFILE_PICTURE_KEEP_ORIGINALS', True)
        
        # Maximum number of profile picture versions to keep per user
        self.max_versions = getattr(settings, 'PROFILE_PICTURE_MAX_VERSIONS', 5)
        
        # File format for optimized images (default: JPEG)
        self.image_format = getattr(settings, 'PROFILE_PICTURE_FORMAT', 'JPEG')
    
    def generate_paths(self, name, user_id=None):
        """
        Generates all paths for the various versions of a profile picture
        
        Args:
            name: Original filename
            user_id: User ID for organizational structure
            
        Returns:
            Dictionary with paths for original and thumbnail versions
        """
        # Get current timestamp for versioning
        now = datetime.datetime.now()
        timestamp = int(now.timestamp())
        
        # Generate unique ID for the file
        unique_id = uuid.uuid4().hex
        
        # Extract file extension, ensuring lowercase
        _, file_ext = os.path.splitext(name)
        file_ext = file_ext.lower()
        
        # Use 'temp' if user_id is not provided
        user_folder = str(user_id) if user_id else 'temp'
        
        # Create path structure
        paths = {
            'unique_id': unique_id,
            'timestamp': timestamp,
            'original': f"{self.base_dir}/original/{user_folder}/{timestamp}_{unique_id}{file_ext}",
            'optimized': f"{self.base_dir}/optimized/{user_folder}/{unique_id}{file_ext}",
            'thumbnails': {}
        }
        
        # Generate thumbnail paths
        for size_name, dimensions in self.sizes.items():
            paths['thumbnails'][size_name] = f"{self.base_dir}/thumbnails/{user_folder}/{size_name}_{unique_id}{file_ext}"
        
        return paths
    
    def get_available_name(self, name, max_length=None):
        """
        Returns a unique filename using the path generation logic.
        For profile pictures, we don't need to check if the file exists 
        because the timestamp + UUID makes it effectively unique.
        """
        # Extract user ID from name if it follows our convention
        # Format is typically like: profiles/avatars/original/123/timestamp_uuid.jpg
        user_id = None
        path_parts = name.split('/')
        
        if len(path_parts) >= 4:
            # Try to extract user_id from path
            try:
                potential_user_id = path_parts[-2]
                # Only use if it's likely a user ID (numeric or a UUID)
                if potential_user_id.isdigit() or len(potential_user_id) > 30:
                    user_id = potential_user_id
            except (IndexError, ValueError):
                pass
        
        # Generate paths based on user ID
        paths = self.generate_paths(name, user_id)
        
        # Return appropriate path based on which subfolder this file belongs to
        if 'original' in name:
            return paths['original']
        elif 'thumbnails' in name:
            # Determine which thumbnail size is being requested
            for size_name in self.sizes.keys():
                if size_name in name:
                    return paths['thumbnails'][size_name]
            # Default to small if size can't be determined
            return paths['thumbnails']['small']
        elif 'optimized' in name:
            return paths['optimized']
        else:
            # Default to the optimized version if path type can't be determined
            return paths['optimized']
    
    def _save(self, name, content):
        """
        Save the file and create additional versions if it's an image
        """
        # Only process image files
        if self._is_image_file(name):
            try:
                # Extract user ID from path
                user_id = self._extract_user_id_from_path(name)
                
                # Generate all paths we'll need
                paths = self.generate_paths(name, user_id)
                
                # Open and process the image
                img = Image.open(content)
                
                # Convert to RGB if needed (e.g., for PNG transparency)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save the original version if enabled
                if self.keep_originals and 'original' in name:
                    # Reset file pointer for reading again
                    content.seek(0)
                    original_path = super()._save(paths['original'], content)
                    
                    # Clean up old versions if we have too many
                    if user_id:
                        self._cleanup_old_versions(user_id)
                
                # Create and save optimized version
                optimized_img = self._resize_image(img, self.max_size)
                optimized_content = self._convert_image_to_content(
                    optimized_img, 
                    self.image_format, 
                    self.image_quality
                )
                
                # Save the optimized version
                optimized_path = super()._save(paths['optimized'], optimized_content)
                
                # Create and save thumbnails
                for size_name, dimensions in self.sizes.items():
                    thumbnail = self._resize_image(img.copy(), dimensions)
                    thumbnail_content = self._convert_image_to_content(
                        thumbnail, 
                        self.image_format, 
                        self.image_quality
                    )
                    
                    # Save this thumbnail
                    thumbnail_path = super()._save(paths['thumbnails'][size_name], thumbnail_content)
                
                # Return the path that was originally requested
                if 'original' in name:
                    return paths['original']
                elif 'thumbnails' in name:
                    # Return the specific thumbnail that was requested
                    for size_name in self.sizes.keys():
                        if size_name in name:
                            return paths['thumbnails'][size_name]
                    # Default to small if size can't be determined
                    return paths['thumbnails']['small']
                else:
                    # Default to the optimized version
                    return paths['optimized']
                
            except Exception as e:
                logger.exception(f"Error processing profile image: {str(e)}")
                # Fall back to standard save if image processing fails
                return super()._save(name, content)
                
        # For non-image files, just save normally
        return super()._save(name, content)
    
    def _is_image_file(self, name):
        """Check if the file appears to be an image based on extension"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        ext = os.path.splitext(name)[1].lower()
        return ext in image_extensions
    
    def _resize_image(self, img, size):
        """Resize an image while maintaining aspect ratio"""
        img.thumbnail(size, Image.LANCZOS)
        return img
    
    def _convert_image_to_content(self, img, format='JPEG', quality=85):
        """Convert a PIL Image to a Django ContentFile"""
        img_io = io.BytesIO()
        img.save(
            img_io,
            format=format,
            quality=quality,
            optimize=True
        )
        return ContentFile(img_io.getvalue())
    
    def _extract_user_id_from_path(self, path):
        """Extract user ID from a file path if possible"""
        parts = path.split('/')
        
        # Try to find the user ID in the path (usually right after 'original', 'thumbnails', etc)
        user_id = None
        for i, part in enumerate(parts):
            if part in ('original', 'thumbnails', 'optimized') and i+1 < len(parts):
                potential_id = parts[i+1]
                if potential_id.isdigit() or len(potential_id) > 30:
                    user_id = potential_id
                    break
                    
        return user_id
    
    def _cleanup_old_versions(self, user_id, keep=None):
        """
        Remove old versions of a user's profile pictures, keeping only the most recent ones
        
        Args:
            user_id: The user's ID
            keep: Number of versions to keep (defaults to self.max_versions)
        """
        if keep is None:
            keep = self.max_versions
            
        # Only clean up if we have a user ID
        if not user_id:
            return
            
        try:
            # Get the list of original files for this user
            original_dir = os.path.join(self.location, 'original', str(user_id))
            
            if not os.path.exists(original_dir):
                return
                
            # List files and sort by timestamp (newest first)
            files = os.listdir(original_dir)
            
            # Sort files by timestamp (files are named: timestamp_uuid.ext)
            files.sort(reverse=True)
            
            # Keep only the specified number of most recent files
            files_to_delete = files[keep:]
            
            # Delete the older files
            for filename in files_to_delete:
                try:
                    file_path = os.path.join(original_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted old profile picture: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete old profile picture {filename}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error during profile picture cleanup for user {user_id}: {str(e)}")
    
    def url(self, name):
        """
        Return the URL for accessing the file.
        Can be overridden to provide CDN URLs, etc.
        """
        return super().url(name)