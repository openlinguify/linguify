from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class QuizzMainView(LoginRequiredMixin, TemplateView):
    """Vue principale pour l'app Quizz"""
    template_name = 'quizz/app.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # App info pour le header
        current_app_info = {
            'name': 'quizz',
            'display_name': 'Quizz',
            'static_icon': '/app-icons/quizz/icon.png',
            'route_path': '/quizz/'
        }
        
        context.update({
            'current_app': current_app_info,
        })
        
        return context