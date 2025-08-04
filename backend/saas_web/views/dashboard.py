"""
Dashboard view - simplified and using services.
"""
from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from app_manager.services import UserAppService


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """Dashboard principal de l'application SaaS"""
    
    def get(self, request):
        # Optimisation: Use service with caching
        from django.core.cache import cache
        
        cache_key = f"user_installed_apps_{request.user.id}"
        installed_apps = cache.get(cache_key)
        
        if installed_apps is None:
            installed_apps = UserAppService.get_user_installed_apps(request.user)
            cache.set(cache_key, installed_apps, 300)  # Cache for 5 minutes
        
        context = {
            'title': _('Dashboard - Open Linguify'),
            'installed_apps': installed_apps,
        }
        
        return render(request, 'saas_web/dashboard.html', context)