
import os
import uuid
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.conf import settings
from PIL import Image
@deconstructible
class SecureUniqueFileStorage(FileSystemStorage):
    """
    Custom storage backend that ensures unique filenames for uploaded files
    and prevents overwriting existing files. Intended for user profile pictures.
    """

    def get_available_name(self, name, max_length=None):
        """
        Returns a unique filename using UUID, preserving the original file extension.
        Prevents overwriting existing files.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        # Generate a unique filename using UUID4
        unique_name = f"{uuid.uuid4().hex}{file_ext.lower()}"
        # Optionally, you can further nest files by user or date for organization
        final_path = os.path.join(dir_name, unique_name)
        # Ensure the file does not exist (shouldn't, but for safety)
        return super().get_available_name(final_path, max_length=max_length)

    def _save(self, name, content):
        # Optionally, add extra security checks here (e.g., scan for viruses)
        return super()._save(name, content)

    def url(self, name):
        """
        Optionally restrict public access to files.
        By default, returns the URL as usual.
        """
        return super().url(name)

# Optionally, you can set a custom location or base_url if needed:
# storage = SecureUniqueFileStorage(location=os.path.join(settings.MEDIA_ROOT, 'profile_pictures'), base_url='/media/profile_pictures/')