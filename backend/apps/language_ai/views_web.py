from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


from django.shortcuts import redirect

class LanguageAIMainView(LoginRequiredMixin, TemplateView):
    """Vue principale pour l'app Language AI - redirige directement vers le chat"""
    
    def get(self, request, *args, **kwargs):
        # Redirection directe vers le chat pour éviter la page intermédiaire
        return redirect('language_ai_web:chat')


class LanguageAIChatView(LoginRequiredMixin, TemplateView):
    """Vue du chat IA pour les conversations"""
    template_name = 'language_ai/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer la langue cible de l'utilisateur
        user = self.request.user
        target_language = getattr(user, 'target_language', 'English')
        
        # App info pour le header
        current_app_info = {
            'name': 'language_ai',
            'display_name': 'AI Chat',
            'static_icon': '/app-icons/language_ai/icon.png',
            'route_path': '/language_ai/chat/'
        }
        
        context.update({
            'current_app': current_app_info,
            'target_language': target_language,
        })
        
        return context