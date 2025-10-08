# app_manager/middleware.py
from django.urls import resolve
from django.core.exceptions import PermissionDenied
from app_manager.models import AppModule

class AppAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_app = resolve(request.path_info).app_name
            if current_app:
                try:
                    user_access = request.user.userappaccess
                    app_module = AppModule.objects.get(name=current_app)
                    
                    has_access = (
                        user_access.is_premium or 
                        user_access.free_selected_app == app_module
                    )
                    
                    if not has_access:
                        raise PermissionDenied("Pas d'accès à cette app")
                        
                except AppModule.DoesNotExist:
                    pass  # L'app n'est pas gérée par app_manager

        response = self.get_response(request)
        return response
