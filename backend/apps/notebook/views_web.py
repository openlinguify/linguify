"""
Vues Django pour l'interface web du Notebook
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

@method_decorator(login_required, name='dispatch')
class NotebookMainView(TemplateView):
    """
    Vue principale pour l'interface notebook
    """
    template_name = 'notebook/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Notebook',
            'debug': self.request.GET.get('debug', 'false').lower() == 'true',
        })
        return context

def notebook_app(request):
    """
    Vue principale pour charger l'application Notebook (legacy)
    """
    context = {
        'debug': request.GET.get('debug', 'false').lower() == 'true',
    }
    return render(request, 'notebook/main.html', context)


@require_http_methods(["GET"])
def get_app_config(request):
    """
    Retourne la configuration de l'application pour le frontend
    """
    config = {
        'features': {
            'sharing': True,
            'tags': True,
            'search': True,
            'export': True,
        },
        'limits': {
            'max_note_size': 1024 * 1024,  # 1MB
            'max_notes': 1000,
        },
        'user_preferences': {
            'theme': request.user.theme if hasattr(request.user, 'theme') else 'light',
            'language': request.user.language if hasattr(request.user, 'language') else 'fr',
        }
    }
    return JsonResponse(config)