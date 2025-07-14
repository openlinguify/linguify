"""
Dashboard view - simplified and using services.
"""
from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ..services.user_app_service import UserAppService


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    """Dashboard principal de l'application SaaS"""
    
    def get(self, request):
        # Use service to get user's installed apps
        installed_apps = UserAppService.get_user_installed_apps(request.user)
        
        context = {
            'title': _('Dashboard - Open Linguify'),
            'installed_apps': installed_apps,
        }
        
        return render(request, 'saas_web/dashboard.html', context)