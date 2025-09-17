# app_manager/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class App(models.Model):
    """
    Represents an application available in the Linguify platform.
    Apps are discovered dynamically from installed modules with __manifest__.py files.
    """
    
    # Technical identifier of the application
    code = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Technical code of the application"
    )
    
    # Display name for users
    display_name = models.CharField(
        max_length=100,
        help_text="Name displayed in the user interface"
    )
    
    # Application description
    description = models.TextField(
        help_text="Description of the application for users"
    )
    
    # Icon for interface
    icon_name = models.CharField(
        max_length=50,
        help_text="Icon name (Lucide React)"
    )
    
    # App theme color
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hexadecimal color for the app (#RRGGBB)"
    )
    
    # Frontend routing URL
    route_path = models.CharField(
        max_length=100,
        help_text="Frontend routing path (e.g., /learning)"
    )
    
    # App category from manifest
    category = models.CharField(
        max_length=100,
        default='Uncategorized',
        help_text="Application category"
    )
    
    # Version from manifest
    version = models.CharField(
        max_length=20,
        default='1.0.0',
        help_text="Application version"
    )
    
    # Whether app is installable (from manifest)
    installable = models.BooleanField(
        default=True,
        help_text="Whether the app can be installed"
    )
    
    # Globally enabled application
    is_enabled = models.BooleanField(
        default=True,
        help_text="Application available on the platform"
    )
    
    # Display order
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in the interface"
    )
    
    # Manifest-based metadata (JSON field for extensibility)
    manifest_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data from the module's __manifest__.py file"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'app_manager'
        ordering = ['order', 'display_name']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
    
    def __str__(self):
        return self.display_name
    
    def clean(self):
        if self.color and not self.color.startswith('#'):
            raise ValidationError({'color': 'Color must start with #'})
    
    def get_current_icon_name(self):
        """Get the current icon name from the manifest file"""
        if hasattr(self, 'manifest_data') and self.manifest_data:
            frontend_components = self.manifest_data.get('frontend_components', {})
            return frontend_components.get('icon', self.icon_name)
        return self.icon_name
    
    def get_static_icon_url(self):
        """Get static icon URL using the service"""
        from .services.app_icon_service import AppIconService
        return AppIconService.get_static_icon_url(self.code)
    
    @classmethod
    def sync_apps(cls):
        """
        Synchronise les applications depuis leurs manifests
        Retourne un résumé des opérations
        """
        summary = {
            'total_discovered': 0,
            'newly_created': 0,
            'updated': 0,
            'errors': []
        }
        
        cls.discover_apps_from_manifests()
        
        # Compter les résultats
        # TODO: Implémenter le comptage des résultats
        
        return summary
    
    @classmethod
    def discover_apps_from_manifests(cls):
        """
        Discover and sync applications from __manifest__.py files.
        This method scans all Django apps for manifest files and creates/updates App records.
        """
        import os
        import importlib.util
        from django.conf import settings
        from django.apps import apps
        
        discovered_apps = []
        
        # Get all installed Django apps
        for app_config in apps.get_app_configs():
            app_name = app_config.name
            
            # Skip Django's built-in apps and non-project apps
            if not app_name.startswith('apps.'):
                continue
            
            # Look for __manifest__.py in the app directory
            try:
                app_path = app_config.path
                manifest_path = os.path.join(app_path, '__manifest__.py')
                
                if os.path.exists(manifest_path):
                    # Load the manifest
                    spec = importlib.util.spec_from_file_location("manifest", manifest_path)
                    manifest_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(manifest_module)
                    
                    # The manifest should be a dictionary assigned to __manifest__
                    manifest_data = None
                    if hasattr(manifest_module, '__manifest__'):
                        manifest_data = getattr(manifest_module, '__manifest__')
                    elif hasattr(manifest_module, '__dict__'):
                        # Fallback: Look for any dictionary with 'name' key
                        for key, value in manifest_module.__dict__.items():
                            if isinstance(value, dict) and 'name' in value:
                                manifest_data = value
                                break
                    
                    if manifest_data:
                        app_code = app_name.split('.')[-1]  # Extract 'course' from 'apps.course'
                        
                        # Extract info from manifest
                        display_name = manifest_data.get('name', app_code.capitalize())
                        description = manifest_data.get('summary', manifest_data.get('description', ''))
                        category = manifest_data.get('category', 'Uncategorized')
                        version = manifest_data.get('version', '1.0.0')
                        installable = manifest_data.get('installable', True)
                        
                        # Get frontend components info
                        frontend_components = manifest_data.get('frontend_components', {})
                        icon_name = frontend_components.get('icon', 'Package')
                        route_path = frontend_components.get('route', f'/{app_code}')
                        
                        # Create or update the App record
                        app_obj, created = cls.objects.update_or_create(
                            code=app_code,
                            defaults={
                                'display_name': display_name,
                                'description': description[:500] if description else '',  # Limit description length
                                'icon_name': icon_name,
                                'route_path': route_path,
                                'category': category,
                                'version': version,
                                'installable': installable,
                                'manifest_data': manifest_data,
                            }
                        )
                        
                        discovered_apps.append({
                            'code': app_code,
                            'name': display_name,
                            'created': created,
                            'app_obj': app_obj
                        })
                            
            except Exception as e:
                print(f"Error processing manifest for {app_name}: {e}")
                continue
        
        return discovered_apps
    
    @classmethod
    def sync_apps(cls):
        """
        Sync all applications from manifests and return a summary.
        """
        discovered = cls.discover_apps_from_manifests()
        
        summary = {
            'total_discovered': len(discovered),
            'newly_created': len([app for app in discovered if app['created']]),
            'updated': len([app for app in discovered if not app['created']]),
            'apps': discovered
        }
        
        return summary

    @classmethod
    def get_ordered_enabled_apps(cls):
        """
        Get all enabled apps ordered by their order field.

        Returns:
            QuerySet: Enabled apps ordered by their order field
        """
        return cls.objects.filter(is_enabled=True).order_by('order', 'display_name')


class UserAppSettings(models.Model):
    """
    User application settings.
    Determines which applications are enabled for each user.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='app_settings'
    )
    
    # Applications enabled by the user
    enabled_apps = models.ManyToManyField(
        App,
        blank=True,
        related_name='enabled_users',
        help_text="Applications enabled by this user"
    )
    
    # Custom app order for this user (JSON field)
    app_order = models.JSONField(
        default=list,
        blank=True,
        help_text="Custom order of apps for this user (array of app display names)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'app_manager'
        verbose_name = 'User App Settings'
        verbose_name_plural = 'User App Settings'
    
    def __str__(self):
        return f"{self.user.username}'s Apps"
    
    def get_enabled_app_codes(self):
        """Returns the list of enabled application codes"""
        return list(self.enabled_apps.values_list('code', flat=True))
    
    def is_app_enabled(self, app_code):
        """Checks if an application is enabled for this user"""
        return self.enabled_apps.filter(code=app_code, is_enabled=True).exists()
    
    def enable_app(self, app_code):
        """Enables an application for this user"""
        try:
            app = App.objects.get(code=app_code, is_enabled=True)
            self.enabled_apps.add(app)
            
            # If there's an existing data retention record for this app, remove it
            # since the user is re-enabling the app before the 30-day period
            try:
                AppDataRetention.objects.filter(
                    user=self.user,
                    app=app,
                    data_deleted=False
                ).delete()
            except Exception as e:
                # Log the error but don't fail the app enabling process
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to delete AppDataRetention records: {e}")

            # Clear the dashboard cache for this user
            from ..services.cache_service import UserAppCacheService
            UserAppCacheService.clear_user_apps_cache_for_user(self.user)

            return True
        except App.DoesNotExist:
            return False
    
    def disable_app(self, app_code):
        """Disables an application for this user"""
        try:
            app = App.objects.get(code=app_code)
            self.enabled_apps.remove(app)
            
            # Create a record for data retention when disabling an app
            try:
                AppDataRetention.objects.create(
                    user=self.user,
                    app=app,
                    disabled_at=timezone.now(),
                    data_expires_at=timezone.now() + timedelta(days=30)
                )
            except Exception as e:
                # Log the error but don't fail the app disabling process
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to create AppDataRetention record: {e}")

            # Clear the dashboard cache for this user
            from ..services.cache_service import UserAppCacheService
            UserAppCacheService.clear_user_apps_cache_for_user(self.user)

            return True
        except App.DoesNotExist:
            return False
    
    def update_app_order(self, app_display_names):
        """
        Updates the custom app order for this user
        
        Args:
            app_display_names: List of app display names in desired order
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate that all provided app names exist and are enabled for this user
            enabled_app_names = list(self.enabled_apps.values_list('display_name', flat=True))
            
            # Filter out any invalid app names
            valid_app_names = [name for name in app_display_names if name in enabled_app_names]
            
            # Add any missing apps that are enabled but not in the provided order
            missing_apps = [name for name in enabled_app_names if name not in valid_app_names]
            final_order = valid_app_names + missing_apps
            
            self.app_order = final_order
            self.save(update_fields=['app_order', 'updated_at'])

            # Clear the dashboard cache for this user since order changed
            from django.core.cache import cache
            cache_key = f"user_installed_apps_{self.user.id}"
            cache.delete(cache_key)

            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update app order: {e}")
            return False
    
    def get_ordered_enabled_apps(self):
        """
        Returns enabled apps in the user's custom order

        Returns:
            QuerySet: Ordered enabled apps
        """
        # Optimized query with only needed fields
        enabled_apps = self.enabled_apps.filter(is_enabled=True).only(
            'id', 'code', 'display_name', 'icon_name', 'route_path', 'color', 'order'
        )
        
        if not self.app_order:
            # Return apps in default order (by order field, then name)
            return enabled_apps.order_by('order', 'display_name')
        
        # Create a dictionary for quick lookup
        apps_dict = {app.display_name: app for app in enabled_apps}
        
        # Build ordered list based on saved order
        ordered_apps = []
        for app_name in self.app_order:
            if app_name in apps_dict:
                ordered_apps.append(apps_dict[app_name])
                del apps_dict[app_name]  # Remove to avoid duplicates
        
        # Add any remaining apps that weren't in the saved order
        remaining_apps = list(apps_dict.values())
        remaining_apps.sort(key=lambda x: (x.order, x.display_name))
        ordered_apps.extend(remaining_apps)
        
        return ordered_apps


class AppDataRetention(models.Model):
    """
    Tracks data retention for disabled applications.
    Ensures user data is preserved for 30 days after app is disabled.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='app_data_retentions',
        help_text="User who disabled the app"
    )
    
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name='data_retentions',
        help_text="Application that was disabled"
    )
    
    disabled_at = models.DateTimeField(
        help_text="When the app was disabled"
    )
    
    data_expires_at = models.DateTimeField(
        help_text="When the user data will be permanently deleted"
    )
    
    data_deleted = models.BooleanField(
        default=False,
        help_text="Whether the data has been permanently deleted"
    )
    
    data_deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the data was permanently deleted"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'app_manager'
        ordering = ['-disabled_at']
        verbose_name = 'App Data Retention'
        verbose_name_plural = 'App Data Retentions'
        # Prevent multiple retention records for the same user/app combination
        unique_together = ['user', 'app']
    
    def __str__(self):
        return f"{self.user.username} - {self.app.display_name} (expires: {self.data_expires_at.date()})"
    
    @property
    def days_until_deletion(self):
        """Returns the number of days until data deletion"""
        if self.data_deleted:
            return 0
        
        delta = self.data_expires_at - timezone.now()
        return max(0, delta.days)
    
    @property
    def is_expired(self):
        """Checks if the retention period has expired"""
        return timezone.now() >= self.data_expires_at
    
    def mark_data_deleted(self):
        """Marks the data as permanently deleted"""
        self.data_deleted = True
        self.data_deleted_at = timezone.now()
        self.save()
    
    @classmethod
    def get_expired_retentions(cls):
        """Returns all retention records that have expired"""
        return cls.objects.filter(
            data_expires_at__lte=timezone.now(),
            data_deleted=False
        )
    
    @classmethod
    def cleanup_expired_data(cls):
        """
        Cleanup method to be called by a scheduled task.
        Marks expired retention records as deleted.
        """
        expired_retentions = cls.get_expired_retentions()
        count = expired_retentions.count()
        
        for retention in expired_retentions:
            retention.mark_data_deleted()
        
        return count
