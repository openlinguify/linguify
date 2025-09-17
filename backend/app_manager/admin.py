# app_manager/admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.utils.html import format_html
from django.contrib import messages
from .models import App, UserAppSettings, AppDataRetention

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'code', 'is_enabled', 'order', 'created_at']
    list_filter = ['is_enabled', 'created_at']
    search_fields = ['display_name', 'code', 'description']
    ordering = ['order', 'display_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'display_name', 'description')
        }),
        ('Appearance', {
            'fields': ('icon_name', 'color', 'route_path')
        }),
        ('Settings', {
            'fields': ('is_enabled', 'order')
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fix-apps/', self.admin_site.admin_view(self.fix_apps_view), name='app_manager_app_fix_apps'),
            path('fix-apps-action/', self.admin_site.admin_view(self.fix_apps_action), name='app_manager_app_fix_apps_action'),
        ]
        return custom_urls + urls
    
    def fix_apps_view(self, request):
        """Vue pour afficher la page de correction des apps"""
        context = {
            'title': 'Correction des Applications',
            'apps': App.objects.all().order_by('order', 'display_name'),
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
        }
        return render(request, 'admin/app_manager/fix_apps.html', context)
    
    def fix_apps_action(self, request):
        """Action pour corriger les apps via AJAX"""
        if not self.has_change_permission(request):
            return JsonResponse({'success': False, 'message': 'Permission refusée'})
        
        try:
            # Logique de correction directe
            app_fixes = {
                'conversation ai': {
                    'display_name': 'Assistant IA',
                    'category': 'Intelligence IA',
                    'description': 'Conversez avec notre IA pour pratiquer la langue et recevoir des corrections personnalisées.',
                    'order': 4,
                },
                'notes': {
                    'display_name': 'Notebook',
                    'category': 'Productivité',
                    'description': 'Prenez des notes intelligentes et organisez votre vocabulaire avec des fonctionnalités avancées.',
                    'order': 1,
                },
                'quiz interactif': {
                    'display_name': 'Quiz',
                    'category': 'Apprentissage',
                    'description': 'Créez et participez à des quiz personnalisés pour tester vos connaissances.',
                    'order': 5,
                },
                'révision': {
                    'display_name': 'Révisions',
                    'category': 'Apprentissage',
                    'description': 'Système de révision avec répétition espacée (Flashcards).',
                    'order': 3,
                }
            }
            
            updated_count = 0
            existing_apps = App.objects.filter(is_enabled=True)
            
            for app in existing_apps:
                app_name_lower = app.display_name.lower()
                if app_name_lower in app_fixes:
                    fixes = app_fixes[app_name_lower]
                    updated = False
                    
                    for key, value in fixes.items():
                        if hasattr(app, key):
                            current_value = getattr(app, key)
                            if current_value != value:
                                setattr(app, key, value)
                                updated = True
                    
                    if updated:
                        app.save()
                        updated_count += 1
            
            return JsonResponse({
                'success': True,
                'message': f'{updated_count} applications mises à jour avec succès',
                'updated_count': updated_count
            })
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})
    
    def changelist_view(self, request, extra_context=None):
        """Ajouter le bouton de correction dans la liste"""
        extra_context = extra_context or {}
        extra_context['fix_apps_url'] = reverse('admin:app_manager_app_fix_apps')
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_object_actions(self, obj):
        """Ajouter des actions personnalisées"""
        return []
    
    def get_list_display_links(self, request, list_display):
        """Personnaliser les liens d'affichage"""
        return super().get_list_display_links(request, list_display)
    
    def response_add(self, request, obj, post_url_continue=None):
        """Personnaliser la réponse après ajout"""
        return super().response_add(request, obj, post_url_continue)
    
    def get_actions(self, request):
        """Ajouter des actions personnalisées"""
        actions = super().get_actions(request)
        if request.user.is_staff:
            actions['fix_apps_action'] = (self.fix_apps_bulk_action, 'fix_apps_action', 'Corriger les applications sélectionnées')
        return actions
    
    def fix_apps_bulk_action(self, request, queryset):
        """Action bulk pour corriger les apps"""
        try:
            from .views import debug_apps
            from django.http import HttpRequest
            
            fake_request = HttpRequest()
            fake_request.method = 'PUT'
            fake_request.user = request.user
            
            response = debug_apps(fake_request)
            
            self.message_user(request, "Applications corrigées avec succès!", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Erreur lors de la correction: {str(e)}", messages.ERROR)
    
    fix_apps_bulk_action.short_description = "🔧 Corriger les applications"

@admin.register(UserAppSettings)
class UserAppSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_enabled_apps_count', 'created_at']
    list_filter = ['created_at', 'enabled_apps']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['enabled_apps']
    
    def get_enabled_apps_count(self, obj):
        return obj.enabled_apps.count()
    get_enabled_apps_count.short_description = 'Enabled Apps Count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('enabled_apps')