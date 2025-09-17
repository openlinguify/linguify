"""
Optimized API views for app manager with fast responses.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
import json
import logging

from ..models import App, UserAppSettings
from ..services.cache_service import UserAppCacheService
from ..services.user_app_service import UserAppService

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_apps_fast_api(request):
    """
    Ultra-fast API to get user's installed apps.
    Uses aggressive caching and minimal data transfer.
    """
    try:
        # Try cache first
        cached_apps = UserAppCacheService.get_user_apps_cache(request.user.id)

        if cached_apps is not None:
            return Response({
                'success': True,
                'apps': cached_apps,
                'cached': True,
                'count': len(cached_apps)
            })

        # Fallback to service if cache miss
        apps = UserAppService.get_user_installed_apps(request.user)
        UserAppCacheService.set_user_apps_cache(request.user.id, apps)

        return Response({
            'success': True,
            'apps': apps,
            'cached': False,
            'count': len(apps)
        })

    except Exception as e:
        logger.error(f"Error in user_apps_fast_api for user {request.user.id}: {e}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60 * 15)  # Cache for 15 minutes
def app_store_categories_api(request):
    """
    Fast API for app store categories.
    Heavily cached since categories don't change often.
    """
    try:
        from ..services.manifest_loader import manifest_loader
        from collections import Counter

        category_mapping = manifest_loader.get_category_mapping()
        category_counts = Counter()
        category_definitions = {}

        for app_code, mapping in category_mapping.items():
            category = mapping['category']
            category_counts[category] += 1
            category_definitions[category] = {
                'label': mapping['label'],
                'icon': mapping['icon']
            }

        return Response({
            'success': True,
            'categories': dict(category_counts),
            'definitions': category_definitions,
        })

    except Exception as e:
        logger.error(f"Error in app_store_categories_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def bulk_app_toggle_api(request):
    """
    API to toggle multiple apps at once for better UX.
    """
    try:
        data = json.loads(request.body)
        app_ids = data.get('app_ids', [])
        action = data.get('action', 'toggle')  # 'install', 'uninstall', or 'toggle'

        if not isinstance(app_ids, list) or not app_ids:
            return JsonResponse({
                'success': False,
                'error': 'app_ids must be a non-empty list'
            }, status=400)

        user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
        results = []

        for app_id in app_ids:
            try:
                app = App.objects.get(id=app_id, is_enabled=True)
                is_currently_installed = user_settings.enabled_apps.filter(id=app_id).exists()

                if action == 'install' and not is_currently_installed:
                    user_settings.enabled_apps.add(app)
                    results.append({'app_id': app_id, 'action': 'installed', 'name': app.display_name})
                elif action == 'uninstall' and is_currently_installed:
                    user_settings.enabled_apps.remove(app)
                    results.append({'app_id': app_id, 'action': 'uninstalled', 'name': app.display_name})
                elif action == 'toggle':
                    if is_currently_installed:
                        user_settings.enabled_apps.remove(app)
                        results.append({'app_id': app_id, 'action': 'uninstalled', 'name': app.display_name})
                    else:
                        user_settings.enabled_apps.add(app)
                        results.append({'app_id': app_id, 'action': 'installed', 'name': app.display_name})

            except App.DoesNotExist:
                results.append({'app_id': app_id, 'error': 'App not found'})

        # Clear cache once for all changes
        UserAppCacheService.clear_user_apps_cache_for_user(request.user)

        return JsonResponse({
            'success': True,
            'results': results,
            'message': f'Processed {len(app_ids)} apps'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in bulk_app_toggle_api for user {request.user.id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def app_installation_status_api(request):
    """
    Fast API to check installation status of specific apps.
    Useful for real-time UI updates.
    """
    try:
        app_ids = request.GET.getlist('app_ids')
        if not app_ids:
            return JsonResponse({
                'success': False,
                'error': 'app_ids parameter required'
            }, status=400)

        user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
        enabled_app_ids = set(user_settings.enabled_apps.values_list('id', flat=True))

        status_map = {}
        for app_id in app_ids:
            try:
                app_id_int = int(app_id)
                status_map[app_id] = app_id_int in enabled_app_ids
            except ValueError:
                status_map[app_id] = False

        return Response({
            'success': True,
            'status': status_map,
            'count': len(enabled_app_ids)
        })

    except Exception as e:
        logger.error(f"Error in app_installation_status_api for user {request.user.id}: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)