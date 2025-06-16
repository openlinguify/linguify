import os
from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates necessary media directories if they do not exist'

    def handle(self, *args, **options):
        # Create main media directory
        self._ensure_dir(settings.MEDIA_ROOT)
        
        # Create profile pictures directory
        profile_dir = getattr(settings, 'PROFILE_PICTURES_DIR', os.path.join(settings.MEDIA_ROOT, 'profile_pictures'))
        self._ensure_dir(profile_dir)
        
        # Create date-based subdirectories for current year/month
        import datetime
        now = datetime.datetime.now()
        year_dir = os.path.join(profile_dir, str(now.year))
        self._ensure_dir(year_dir)
        
        month_dir = os.path.join(year_dir, f"{now.month:02d}")
        self._ensure_dir(month_dir)
        
        self.stdout.write(self.style.SUCCESS('Successfully created all required media directories'))
    
    def _ensure_dir(self, directory):
        """Create directory if it doesn't exist"""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                self.stdout.write(f"Created directory: {directory}")
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create directory {directory}: {str(e)}"))
                logger.error(f"Failed to create directory {directory}: {str(e)}")
        else:
            self.stdout.write(f"Directory already exists: {directory}")