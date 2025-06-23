from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class LanguageAIMainView(LoginRequiredMixin, TemplateView):
    """Vue principale pour l'app Language AI"""
    template_name = 'language_ai/app.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # App info pour le header
        current_app_info = {
            'name': 'language_ai',
            'display_name': 'Conversation AI',
            'static_icon': '/app-icons/language_ai/icon.png',
            'route_path': '/conversation-ai/'
        }
        
        context.update({
            'current_app': current_app_info,
        })
        
        return context