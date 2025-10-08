"""
Service for managing user applications and settings.
"""
import logging
from django.utils import timezone
from datetime import timedelta
from ..models import App, UserAppSettings
from .app_icon_service import AppIconService
from .manifest_loader import manifest_loader

logger = logging.getLogger(__name__)


class UserAppService:
    """Service for managing user applications and their settings."""
    
    @classmethod
    def get_or_create_user_settings(cls, user):
        """
        Get or create user app settings with default apps if needed.
        
        Args:
            user: The user instance
            
        Returns:
            UserAppSettings: The user's app settings
        """
        user_settings, created = UserAppSettings.objects.get_or_create(user=user)
        
        # If user has no apps enabled, enable some default apps
        if created or user_settings.enabled_apps.count() == 0:
            default_apps = App.objects.filter(is_enabled=True, installable=True)[:3]
            if default_apps.exists():
                user_settings.enabled_apps.set(default_apps)
                logger.info(f"Enabled {default_apps.count()} default apps for user {user.id}")
        
        return user_settings
    
    @classmethod
    def get_user_installed_apps(cls, user):
        """
        Get formatted list of user's installed apps with enriched data.
        
        Args:
            user: The user instance
            
        Returns:
            list: List of app dictionaries with display data
        """
        user_settings = cls.get_or_create_user_settings(user)
        enabled_apps = user_settings.get_ordered_enabled_apps()
        
        installed_apps = []
        for app in enabled_apps:
            app_data = cls._format_app_data(app)
            installed_apps.append(app_data)
        
        return installed_apps
    
    @classmethod
    def get_user_apps_with_registry_info(cls, user):
        """
        Get user apps with registry information for settings page.
        
        Args:
            user: The user instance
            
        Returns:
            tuple: (user_apps_list, app_recommendations_list)
        """
        user_apps = []
        app_recommendations = []
        
        try:
            from core.app_registry import get_app_registry
            from core.app_synergies import get_synergy_manager
            
            # Use optimized registry
            registry = get_app_registry()
            synergy_manager = get_synergy_manager()
            
            user_settings = cls.get_or_create_user_settings(user)
            
            # Get all registered apps
            all_registered_apps = registry.discover_all_apps()
            enabled_app_codes = list(user_settings.enabled_apps.values_list('code', flat=True))
            
            # Process user's enabled apps with enriched information
            for app in user_settings.enabled_apps.all():
                app_code = app.code
                registry_info = all_registered_apps.get(app_code, {})
                
                app_data = {
                    'display_name': app.display_name,
                    'route_path': app.route_path,
                    'icon_class': AppIconService.get_icon_class(app.icon_name),
                    'last_used': timezone.now() - timedelta(hours=2),  # Simulated - could be real data
                    'usage_count': 42,  # Simulated - could be real data
                    'status': 'active',
                    'registry_status': registry_info.get('status', 'unknown'),
                    'has_config': bool(registry_info.get('config_class')),
                    'version': registry_info.get('version', '1.0.0'),
                }
                user_apps.append(app_data)
            
            # Generate recommendations based on synergies
            if user_apps:
                try:
                    recommendations = synergy_manager.get_recommendations_for_user(
                        enabled_app_codes, 
                        limit=3
                    )
                    
                    for rec_app_code in recommendations:
                        try:
                            rec_app = App.objects.get(code=rec_app_code, is_enabled=True)
                            app_recommendations.append({
                                'display_name': rec_app.display_name,
                                'description': rec_app.description[:100] + '...' if rec_app.description else '',
                                'icon_class': AppIconService.get_icon_class(rec_app.icon_name),
                                'synergy_score': 0.85,  # Could be calculated
                                'reason': 'Complements your current apps',
                            })
                        except App.DoesNotExist:
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error getting app recommendations: {e}")
                    
        except ImportError as e:
            logger.warning(f"Registry system not available: {e}")
        except Exception as e:
            logger.error(f"Error getting user apps with registry info: {e}")
            
        return user_apps, app_recommendations
    
    @classmethod
    def _format_app_data(cls, app):
        """
        Format app data for display using manifest data for translations.

        Args:
            app: App model instance

        Returns:
            dict: Formatted app data
        """
        # Get app info from manifest for translations
        app_info = manifest_loader.get_app_info(app.code)

        # Use database route_path primarily, fall back to manifest if empty
        route_path = app.route_path
        if not route_path:
            route_path = app_info.get('route_path', f'/{app.code}/')

        # Ensure route_path ends with slash for consistency
        if not route_path.endswith('/'):
            route_path += '/'

        return {
            'name': app.code,
            'display_name': app_info.get('display_name', app.display_name),
            'url': route_path,
            'icon': app.icon_name,
            'static_icon': AppIconService.get_static_icon_url(app.code),
            'color_gradient': AppIconService.get_color_gradient(app.color),
        }

    @classmethod
    def toggle_app(cls, user, app_id):
        """
        Toggle an app for a user (enable/disable).

        Args:
            user: The user instance
            app_id: ID of the app to toggle

        Returns:
            dict: Result of the toggle operation
        """
        try:
            app = App.objects.get(id=app_id, is_enabled=True)
            user_settings = cls.get_or_create_user_settings(user)

            if user_settings.enabled_apps.filter(id=app_id).exists():
                # Disable app
                user_settings.enabled_apps.remove(app)
                is_enabled = False
                action = 'disabled'
            else:
                # Enable app
                user_settings.enabled_apps.add(app)
                is_enabled = True
                action = 'enabled'

            # Clear cache
            from .cache_service import UserAppCacheService
            UserAppCacheService.clear_user_apps_cache_for_user(user)

            return {
                'success': True,
                'is_enabled': is_enabled,
                'action': action,
                'app_name': app.display_name
            }

        except App.DoesNotExist:
            return {
                'success': False,
                'error': 'App not found or disabled'
            }
        except Exception as e:
            logger.error(f"Error toggling app {app_id} for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @classmethod
    def get_user_enabled_apps(cls, user):
        """
        Get user's enabled apps (alias for compatibility).

        Args:
            user: The user instance

        Returns:
            list: List of enabled apps
        """
        return cls.get_user_installed_apps(user)

    @classmethod
    def bulk_toggle_apps(cls, user, app_configs):
        """
        Toggle multiple apps at once.

        Args:
            user: The user instance
            app_configs: List of app configurations

        Returns:
            dict: Results of bulk toggle operation
        """
        results = []
        user_settings = cls.get_or_create_user_settings(user)

        for config in app_configs:
            app_id = config.get('app_id')
            action = config.get('action', 'toggle')

            try:
                app = App.objects.get(id=app_id, is_enabled=True)
                is_currently_enabled = user_settings.enabled_apps.filter(id=app_id).exists()

                if action == 'enable' and not is_currently_enabled:
                    user_settings.enabled_apps.add(app)
                    results.append({'app_id': app_id, 'action': 'enabled', 'success': True})
                elif action == 'disable' and is_currently_enabled:
                    user_settings.enabled_apps.remove(app)
                    results.append({'app_id': app_id, 'action': 'disabled', 'success': True})
                elif action == 'toggle':
                    if is_currently_enabled:
                        user_settings.enabled_apps.remove(app)
                        results.append({'app_id': app_id, 'action': 'disabled', 'success': True})
                    else:
                        user_settings.enabled_apps.add(app)
                        results.append({'app_id': app_id, 'action': 'enabled', 'success': True})
                else:
                    results.append({'app_id': app_id, 'action': 'no_change', 'success': True})

            except App.DoesNotExist:
                results.append({'app_id': app_id, 'error': 'App not found', 'success': False})
            except Exception as e:
                results.append({'app_id': app_id, 'error': str(e), 'success': False})

        # Clear cache once for all changes
        from .cache_service import UserAppCacheService
        UserAppCacheService.clear_user_apps_cache_for_user(user)

        return {
            'success': True,
            'results': results,
            'total_processed': len(app_configs)
        }

    @classmethod
    def get_user_app_settings(cls, user):
        """
        Get user app settings (alias for compatibility).

        Args:
            user: The user instance

        Returns:
            UserAppSettings: The user's app settings
        """
        return cls.get_or_create_user_settings(user)