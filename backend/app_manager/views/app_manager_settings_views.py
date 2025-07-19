from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.views import View
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from ..models.app_manager_models import App, UserAppSettings
from ..serializers.app_manager_settings_serializers import UserAppSettingsSerializer
from ..services.user_app_service import UserAppService
from ..services.manifest_loader import manifest_loader
from ..mixins import SettingsContextMixin


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


@method_decorator(login_required, name='dispatch')
class AppManagerSettingsView(View, SettingsContextMixin):
    """Vue pour les paramètres de gestion des applications"""
    
    def get(self, request):
        # Obtenir les apps installées de l'utilisateur avec les infos complètes
        user_settings = UserAppService.get_or_create_user_settings(request.user)
        installed_apps = user_settings.enabled_apps.filter(is_enabled=True)
        
        # Enrichir avec les données du manifest
        enriched_apps = []
        for app in installed_apps:
            app_info = manifest_loader.get_app_info(app.code)
            enriched_apps.append({
                'id': app.id,
                'code': app.code,
                'display_name': app_info.get('display_name', app.display_name),
                'version': app_info.get('version', '1.0.0'),
                'category': app_info.get('category_label', 'Application'),
                'static_icon': f"/app-icons/{app.code}/icon.png" if app_info.get('has_static_icon') else None,
                'description': app_info.get('description', ''),
                'author': app_info.get('author', ''),
            })
        
        # Utiliser le mixin pour avoir la sidebar cohérente
        context = self.get_settings_context(
            user=request.user,
            active_tab_id='app_manager',
            page_title='Gestionnaire d\'Applications',
            page_subtitle='Gérez vos applications installées et configurez l\'App Store'
        )
        
        # Ajouter les données spécifiques à cette page
        context.update({
            'installed_apps': enriched_apps,
            'total_installed': len(enriched_apps),
        })
        
        return render(request, 'app_manager/app_manager_settings_full.html', context)
    
    def post(self, request):
        # Traiter les paramètres soumis
        setting_type = request.POST.get('setting_type')
        
        if setting_type == 'app_store':
            # Traiter les paramètres de l'App Store
            # TODO: Implémenter la logique de sauvegarde
            pass
        elif setting_type == 'app_security':
            # Traiter les paramètres de sécurité
            # TODO: Implémenter la logique de sauvegarde
            pass
        
        # Rediriger vers la même page après traitement
        return self.get(request)