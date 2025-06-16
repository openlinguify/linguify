from django.shortcuts import render, redirect
from django.views import View
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.conf import settings


class LandingView(View):
    """Page d'accueil publique"""
    def get(self, request):
        # Rediriger vers le dashboard si l'utilisateur est connecté
        if request.user.is_authenticated:
            return redirect('saas_web:dashboard')
            
        context = {
            'title': _('Open Linguify - Apprenez les langues'),
            'meta_description': _('Plateforme open source pour apprendre les langues'),
        }
        return render(request, 'public_web/landing.html', context)


class FeaturesView(View):
    """Page des fonctionnalités"""
    def get(self, request):
        context = {
            'title': _('Fonctionnalités - Open Linguify'),
            'meta_description': _('Découvrez toutes les fonctionnalités de Open Linguify'),
        }
        return render(request, 'public_web/features.html', context)


class AboutView(View):
    """Page à propos"""
    def get(self, request):
        context = {
            'title': _('À propos - Open Linguify'),
            'meta_description': _('En savoir plus sur Open Linguify'),
        }
        return render(request, 'public_web/about.html', context)


class CareersView(View):
    """Page carrières"""
    def get(self, request):
        context = {
            'title': _('Carrières - Open Linguify'),
            'meta_description': _('Rejoignez l\'équipe Open Linguify'),
        }
        return render(request, 'public_web/careers.html', context)


class BlogView(View):
    """Page blog"""
    def get(self, request):
        context = {
            'title': _('Blog - Open Linguify'),
            'meta_description': _('Actualités et conseils pour apprendre les langues'),
        }
        return render(request, 'public_web/blog.html', context)


class ContactView(View):
    """Page contact"""
    def get(self, request):
        context = {
            'title': _('Contact - Open Linguify'),
            'meta_description': _('Contactez l\'équipe Open Linguify'),
        }
        return render(request, 'public_web/contact.html', context)


class PrivacyView(View):
    """Page politique de confidentialité"""
    def get(self, request):
        context = {
            'title': _('Politique de confidentialité - Open Linguify'),
        }
        return render(request, 'public_web/privacy.html', context)


class TermsView(View):
    """Page conditions d'utilisation"""
    def get(self, request):
        context = {
            'title': _('Conditions d\'utilisation - Open Linguify'),
        }
        return render(request, 'public_web/legal/terms.html', context)


# Views pour les pages de présentation des apps
class AppsView(View):
    """Page listant toutes les applications"""
    def get(self, request):
        context = {
            'title': _('Applications - Open Linguify'),
            'meta_description': _('Découvrez toutes les applications Open Linguify'),
        }
        return render(request, 'public_web/apps/index.html', context)


class AppDetailView(View):
    """Vue générique pour la présentation d'une app"""
    template_name = None
    app_name = None
    
    def get(self, request):
        context = {
            'title': f'{self.app_name} - Open Linguify',
            'meta_description': f'Découvrez {self.app_name} sur Open Linguify',
        }
        return render(request, self.template_name, context)


# Vues spécifiques pour chaque app
class AppCoursesView(AppDetailView):
    template_name = 'public_web/apps/courses.html'
    app_name = 'Courses'


class AppRevisionView(AppDetailView):
    template_name = 'public_web/apps/revision.html'
    app_name = 'Revision'


class AppNotebookView(AppDetailView):
    template_name = 'public_web/apps/notebook.html'
    app_name = 'Notebook'


class AppQuizzView(AppDetailView):
    template_name = 'public_web/apps/quizz.html'
    app_name = 'Quiz'


class AppLanguageAIView(AppDetailView):
    template_name = 'public_web/apps/language_ai.html'
    app_name = 'Language AI'