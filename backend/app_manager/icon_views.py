"""
Views pour servir les icônes d'applications style Odoo
"""
import os
from django.http import FileResponse, Http404
from django.apps import apps
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control


@method_decorator(cache_control(max_age=86400), name='dispatch')  # Cache 24h
class AppIconView(View):
    """
    Sert les icônes des applications style Odoo
    URL: /app-icons/{app_name}/icon.png
    """
    
    def get(self, request, app_name, filename):
        """Servir l'icône d'une app spécifique"""
        
        # Vérifier que le fichier demandé est bien une icône
        if not filename.endswith(('.png', '.svg', '.jpg', '.jpeg')):
            raise Http404("Invalid file type")
        
        # Trouver l'app Django correspondante
        app_config = None
        for config in apps.get_app_configs():
            if config.label == app_name or config.name.endswith(app_name):
                app_config = config
                break
        
        if not app_config:
            raise Http404(f"App '{app_name}' not found")
        
        # Construire le chemin vers l'icône
        icon_path = os.path.join(app_config.path, 'static', 'description', filename)
        
        if not os.path.exists(icon_path):
            raise Http404(f"Icon '{filename}' not found for app '{app_name}'")
        
        # Servir le fichier
        try:
            return FileResponse(
                open(icon_path, 'rb'),
                content_type=self._get_content_type(filename)
            )
        except IOError:
            raise Http404("Icon file cannot be read")
    
    def _get_content_type(self, filename):
        """Détermine le content-type basé sur l'extension"""
        ext = filename.lower().split('.')[-1]
        content_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'svg': 'image/svg+xml',
        }
        return content_types.get(ext, 'application/octet-stream')