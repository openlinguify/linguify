# app_manager/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from .models import App, UserAppSettings
from .serializers import AppSerializer, UserAppSettingsSerializer, AppToggleSerializer

class AppListView(generics.ListAPIView):
    """
    List all available applications with deduplication
    """
    serializer_class = AppSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get all enabled apps
        apps = App.objects.filter(is_enabled=True).order_by('display_name', '-id')
        
        # Deduplicate by display_name - keep the one with highest ID (most recent)
        seen_names = set()
        unique_apps = []
        
        for app in apps:
            if app.display_name not in seen_names:
                unique_apps.append(app)
                seen_names.add(app.display_name)
        
        # Return as queryset - we'll filter the IDs
        unique_ids = [app.id for app in unique_apps]
        return App.objects.filter(id__in=unique_ids).order_by('order', 'display_name')

class UserAppSettingsView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user app settings
    """
    serializer_class = UserAppSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Get or create user app settings
        user_settings, created = UserAppSettings.objects.get_or_create(
            user=self.request.user
        )
        
        # If newly created, enable all apps by default
        if created:
            all_apps = App.objects.filter(is_enabled=True)
            user_settings.enabled_apps.set(all_apps)
        
        return user_settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_app(request):
    """
    Toggle an app on/off for the current user
    """
    serializer = AppToggleSerializer(data=request.data)
    if serializer.is_valid():
        app_code = serializer.validated_data['app_code']
        enabled = serializer.validated_data['enabled']
        
        # Get or create user app settings
        user_settings, created = UserAppSettings.objects.get_or_create(
            user=request.user
        )
        
        if enabled:
            success = user_settings.enable_app(app_code)
            message = f"App '{app_code}' enabled successfully" if success else f"Failed to enable app '{app_code}'"
        else:
            success = user_settings.disable_app(app_code)
            message = f"App '{app_code}' disabled successfully" if success else f"Failed to disable app '{app_code}'"
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'enabled_apps': user_settings.get_enabled_app_codes()
            })
        else:
            return Response({
                'success': False,
                'message': message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_enabled_apps(request):
    """
    Get list of apps enabled for the current user
    """
    user_settings, created = UserAppSettings.objects.get_or_create(
        user=request.user
    )
    
    # If newly created, enable all apps by default
    if created:
        all_apps = App.objects.filter(is_enabled=True)
        user_settings.enabled_apps.set(all_apps)
    
    enabled_apps = user_settings.enabled_apps.filter(is_enabled=True)
    serializer = AppSerializer(enabled_apps, many=True)
    
    return Response({
        'enabled_apps': serializer.data,
        'enabled_app_codes': user_settings.get_enabled_app_codes()
    })

@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def debug_apps(request):
    """
    Debug view to see all app data, add missing apps, and fix existing ones
    """
    if request.method == 'PUT' and request.user.is_staff:
        # Corriger seulement les apps activées (ne pas toucher à celles en développement)
        app_fixes = {
            'conversation ai': {
                'display_name': 'Assistant IA',
                'category': 'Intelligence IA',
                'description': 'Conversez avec notre IA pour pratiquer la langue et recevoir des corrections personnalisées.',
                'order': 4,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '🤖',
                        'description': 'Assistant IA pour l\'apprentissage des langues',
                        'route': '/language-ai/'
                    },
                    'technical_info': {
                        'web_url': '/language-ai/',
                        'api_url': '/api/v1/language_ai/'
                    }
                }
            },
            'notes': {
                'display_name': 'Notebook',
                'category': 'Productivité',
                'description': 'Prenez des notes intelligentes et organisez votre vocabulaire avec des fonctionnalités avancées.',
                'is_enabled': True,
                'order': 1,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '📓',
                        'description': 'Notebook intelligent pour l\'apprentissage',
                        'route': '/notebook/'
                    },
                    'technical_info': {
                        'web_url': '/notebook/',
                        'api_url': '/api/v1/notebook/'
                    }
                }
            },
            'quiz interactif': {
                'display_name': 'Quiz',
                'category': 'Apprentissage',
                'description': 'Créez et participez à des quiz personnalisés pour tester vos connaissances.',
                'is_enabled': True,
                'order': 5,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '❓',
                        'description': 'Quiz interactifs et personnalisés',
                        'route': '/quiz/'
                    },
                    'technical_info': {
                        'web_url': '/quiz/',
                        'api_url': '/api/v1/quizz/'
                    }
                }
            },
            'révision': {
                'display_name': 'Révisions',
                'category': 'Apprentissage',
                'description': 'Système de révision avec répétition espacée (Flashcards).',
                'is_enabled': True,
                'order': 3,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '🃏',
                        'description': 'Révisions et flashcards',
                        'route': '/revision/'
                    },
                    'technical_info': {
                        'web_url': '/revision/',
                        'api_url': '/api/v1/revision/'
                    }
                }
            }
        }
        
        updated_count = 0
        # Ne corriger que les apps activées
        existing_apps = App.objects.filter(is_enabled=True)
        
        for app in existing_apps:
            app_name_lower = app.display_name.lower()
            if app_name_lower in app_fixes:
                fixes = app_fixes[app_name_lower]
                updated = False
                
                for key, value in fixes.items():
                    current_value = getattr(app, key)
                    if current_value != value:
                        setattr(app, key, value)
                        updated = True
                
                if updated:
                    app.save()
                    updated_count += 1
        
        return Response({
            'success': True,
            'message': f'{updated_count} apps mises à jour avec les bonnes données',
            'updated_count': updated_count
        })
    
    if request.method == 'POST' and request.user.is_staff:
        # Ajouter toutes les apps essentielles de Linguify
        missing_apps = [
            {
                'code': 'notebook',
                'display_name': 'Notebook',
                'description': 'Prenez des notes intelligentes et organisez votre vocabulaire avec des fonctionnalités avancées.',
                'category': 'Productivité',
                'is_enabled': True,
                'is_default': True,
                'order': 1,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '📓',
                        'description': 'Notebook intelligent pour l\'apprentissage',
                        'route': '/notebook/'
                    },
                    'technical_info': {
                        'web_url': '/notebook/',
                        'api_url': '/api/v1/notebook/'
                    }
                }
            },
            {
                'code': 'course',
                'display_name': 'Cours',
                'description': 'Accédez à des cours structurés avec des exercices interactifs et des évaluations personnalisées.',
                'category': 'Apprentissage',
                'is_enabled': True,
                'is_default': True,
                'order': 2,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '📚',
                        'description': 'Cours structurés et interactifs',
                        'route': '/course/'
                    },
                    'technical_info': {
                        'web_url': '/course/',
                        'api_url': '/api/v1/course/'
                    }
                }
            },
            {
                'code': 'revision',
                'display_name': 'Révisions',
                'description': 'Système de révision avec répétition espacée (Flashcards).',
                'category': 'Apprentissage',
                'is_enabled': True,
                'is_default': True,
                'order': 3,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '🃏',
                        'description': 'Révisions et flashcards',
                        'route': '/revision/'
                    },
                    'technical_info': {
                        'web_url': '/revision/',
                        'api_url': '/api/v1/revision/'
                    }
                }
            },
            {
                'code': 'language_ai',
                'display_name': 'Assistant IA',
                'description': 'Conversez avec notre IA pour pratiquer la langue et recevoir des corrections personnalisées.',
                'category': 'Intelligence IA',
                'is_enabled': True,
                'is_default': False,
                'order': 4,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '🤖',
                        'description': 'Assistant IA pour l\'apprentissage des langues',
                        'route': '/language-ai/'
                    },
                    'technical_info': {
                        'web_url': '/language-ai/',
                        'api_url': '/api/v1/language_ai/'
                    }
                }
            },
            {
                'code': 'quizz',
                'display_name': 'Quiz',
                'description': 'Créez et participez à des quiz personnalisés pour tester vos connaissances.',
                'category': 'Apprentissage',
                'is_enabled': True,
                'is_default': False,
                'order': 5,
                'manifest_data': {
                    'frontend_components': {
                        'icon': '❓',
                        'description': 'Quiz interactifs et personnalisés',
                        'route': '/quiz/'
                    },
                    'technical_info': {
                        'web_url': '/quiz/',
                        'api_url': '/api/v1/quizz/'
                    }
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for app_data in missing_apps:
            app, created = App.objects.get_or_create(
                code=app_data['code'],
                defaults=app_data
            )
            if created:
                created_count += 1
            else:
                # Mettre à jour les apps existantes avec les nouvelles données
                updated = False
                for key, value in app_data.items():
                    if key != 'code' and getattr(app, key) != value:
                        setattr(app, key, value)
                        updated = True
                
                if updated:
                    app.save()
                    updated_count += 1
        
        # Corriger les catégories des apps existantes qui ne correspondent pas
        category_fixes = {
            'conversation ai': {'category': 'Intelligence IA', 'display_name': 'Assistant IA'},
            'notes': {'category': 'Productivité', 'display_name': 'Notebook'},
            'quiz interactif': {'category': 'Apprentissage', 'display_name': 'Quiz'},
            'révision': {'category': 'Apprentissage'}
        }
        
        existing_apps = App.objects.all()
        for app in existing_apps:
            app_name_lower = app.display_name.lower()
            if app_name_lower in category_fixes:
                fixes = category_fixes[app_name_lower]
                updated = False
                for key, value in fixes.items():
                    if getattr(app, key) != value:
                        setattr(app, key, value)
                        updated = True
                
                if updated:
                    app.save()
                    updated_count += 1
        
        return Response({
            'success': True,
            'message': f'{created_count} nouvelles apps créées, {updated_count} apps mises à jour',
            'created_count': created_count,
            'updated_count': updated_count
        })
    
    user_settings, created = UserAppSettings.objects.get_or_create(
        user=request.user
    )
    
    all_apps = App.objects.all().order_by('code')
    enabled_apps = user_settings.enabled_apps.all()
    
    app_data = []
    for app in all_apps:
        app_data.append({
            'id': app.id,
            'code': app.code,
            'display_name': app.display_name,
            'is_enabled': app.is_enabled,
            'user_has_enabled': app in enabled_apps,
            'category': app.category
        })
    
    return Response({
        'total_apps': all_apps.count(),
        'enabled_by_user': enabled_apps.count(),
        'apps': app_data,
        'enabled_app_codes': user_settings.get_enabled_app_codes(),
        'user_created': created,
        'can_add_apps': request.user.is_staff
    })


@method_decorator(login_required, name='dispatch')
class AppStoreView(View):
    """Vue de l'App Store pour gérer les applications"""
    def get(self, request):
        # Récupérer toutes les apps disponibles
        apps = App.objects.filter(is_enabled=True)
        
        # Récupérer les settings utilisateur ou les créer
        user_settings, created = UserAppSettings.objects.get_or_create(user=request.user)
        enabled_app_ids = user_settings.enabled_apps.values_list('id', flat=True)
        
        available_apps = []
        for app in apps:
            available_apps.append({
                'id': app.id,
                'name': app.code,
                'display_name': app.display_name,
                'description': app.description,
                'icon': app.icon_name or 'bi-app',
                'color_gradient': f'linear-gradient(135deg, {app.color} 0%, {app.color}80 100%)',
                'category': app.category,
                'route_path': app.route_path,
                'is_installed': app.id in enabled_app_ids,
                'installable': app.installable,
            })
        
        context = {
            'title': _('App Store - Open Linguify'),
            'apps': available_apps,
            'enabled_app_ids': list(enabled_app_ids),
        }
        return render(request, 'app_manager/app_store.html', context)