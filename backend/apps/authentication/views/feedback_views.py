# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# Vues pour le système de feedback utilisateur

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, DetailView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.forms import ModelForm, FileInput, Textarea, Select, TextInput
from django.core.exceptions import PermissionDenied
from django.utils import timezone
import logging
import json

from ..models import UserFeedback, FeedbackAttachment, FeedbackResponse
from ..models import FEEDBACK_TYPE_CHOICES, FEEDBACK_PRIORITY_CHOICES, FEEDBACK_CATEGORY_CHOICES

logger = logging.getLogger(__name__)


class FeedbackForm(ModelForm):
    """Formulaire pour créer/modifier un feedback"""

    class Meta:
        model = UserFeedback
        fields = [
            'title', 'feedback_type', 'category', 'priority', 'description',
            'steps_to_reproduce', 'expected_behavior', 'actual_behavior',
            'page_url', 'screenshot'
        ]

        widgets = {
            'title': TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Brief summary of your feedback'),
                'maxlength': 200
            }),
            'feedback_type': Select(attrs={'class': 'form-select'}),
            'category': Select(attrs={'class': 'form-select'}),
            'priority': Select(attrs={'class': 'form-select'}),
            'description': Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Please provide detailed information about your feedback')
            }),
            'steps_to_reproduce': Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('For bug reports: Step 1, Step 2, Step 3...')
            }),
            'expected_behavior': Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': _('What should have happened?')
            }),
            'actual_behavior': Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': _('What actually happened?')
            }),
            'page_url': TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL where the issue occurred (optional)')
            }),
            'screenshot': FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels
        self.fields['title'].label = _('Title')
        self.fields['feedback_type'].label = _('Type')
        self.fields['category'].label = _('Category')
        self.fields['priority'].label = _('Priority')
        self.fields['description'].label = _('Description')
        self.fields['steps_to_reproduce'].label = _('Steps to Reproduce (for bugs)')
        self.fields['expected_behavior'].label = _('Expected Behavior')
        self.fields['actual_behavior'].label = _('Actual Behavior')
        self.fields['page_url'].label = _('Page URL')
        self.fields['screenshot'].label = _('Screenshot (optional)')

        # Définir des champs optionnels selon le type
        self.fields['steps_to_reproduce'].required = False
        self.fields['expected_behavior'].required = False
        self.fields['actual_behavior'].required = False
        self.fields['page_url'].required = False
        self.fields['screenshot'].required = False


@method_decorator(login_required, name='dispatch')
class FeedbackListView(ListView):
    """Vue liste des feedbacks de l'utilisateur"""
    model = UserFeedback
    template_name = 'authentication/feedback/feedback_list.html'
    context_object_name = 'feedbacks'
    paginate_by = 10

    def get_queryset(self):
        """Récupérer seulement les feedbacks de l'utilisateur connecté"""
        queryset = UserFeedback.objects.filter(
            user=self.request.user
        ).select_related(
            'assigned_to'
        ).prefetch_related(
            'responses', 'attachments'
        ).order_by('-created_at')

        # Filtrage par statut
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filtrage par type
        type_filter = self.request.GET.get('type')
        if type_filter:
            queryset = queryset.filter(feedback_type=type_filter)

        # Recherche
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistiques pour l'utilisateur
        user_feedbacks = UserFeedback.objects.filter(user=self.request.user)
        context['stats'] = {
            'total': user_feedbacks.count(),
            'new': user_feedbacks.filter(status='new').count(),
            'in_progress': user_feedbacks.filter(status='in_progress').count(),
            'resolved': user_feedbacks.filter(status='resolved').count(),
            'bugs': user_feedbacks.filter(feedback_type='bug_report').count(),
            'features': user_feedbacks.filter(feedback_type='feature_request').count(),
        }

        # Options de filtrage
        context['status_choices'] = UserFeedback._meta.get_field('status').choices
        context['type_choices'] = UserFeedback._meta.get_field('feedback_type').choices

        # Filtres actifs
        context['active_filters'] = {
            'status': self.request.GET.get('status', ''),
            'type': self.request.GET.get('type', ''),
            'search': self.request.GET.get('search', ''),
        }

        return context


@method_decorator(login_required, name='dispatch')
class FeedbackDetailView(DetailView):
    """Vue détaillée d'un feedback"""
    model = UserFeedback
    template_name = 'authentication/feedback/feedback_detail.html'
    context_object_name = 'feedback'

    def get_object(self):
        """Seuls les propriétaires peuvent voir leurs feedbacks"""
        feedback = get_object_or_404(
            UserFeedback.objects.select_related('user', 'assigned_to'),
            pk=self.kwargs['pk'],
            user=self.request.user
        )
        return feedback

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feedback = self.object

        # Responses publiques (visibles par l'utilisateur)
        context['responses'] = feedback.responses.filter(
            is_internal=False
        ).select_related('author').order_by('created_at')

        # Attachments
        context['attachments'] = feedback.attachments.all()

        # Informations de statut avec couleurs
        context['status_info'] = feedback.get_status_display_with_color()
        context['priority_info'] = feedback.get_priority_display_with_color()

        return context


@method_decorator(login_required, name='dispatch')
class FeedbackCreateView(CreateView):
    """Vue pour créer un nouveau feedback"""
    model = UserFeedback
    form_class = FeedbackForm
    template_name = 'authentication/feedback/feedback_create.html'
    success_url = reverse_lazy('authentication:feedback_list')

    def form_valid(self, form):
        """Assigner l'utilisateur connecté au feedback"""
        form.instance.user = self.request.user

        # Collecter des informations techniques automatiquement
        form.instance.browser_info = self.get_browser_info()
        if not form.instance.page_url:
            form.instance.page_url = self.request.META.get('HTTP_REFERER', '')

        response = super().form_valid(form)

        messages.success(
            self.request,
            _('Your feedback has been submitted successfully. Thank you for helping us improve!')
        )

        return response

    def get_browser_info(self):
        """Collecter les informations du navigateur"""
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        remote_addr = self.request.META.get('REMOTE_ADDR', '')

        return f"User Agent: {user_agent}\\nIP: {remote_addr}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Submit Feedback')

        # Informations d'aide pour les types
        context['type_help'] = {
            'bug_report': _('Report a problem or error you encountered'),
            'feature_request': _('Suggest a new feature or enhancement'),
            'improvement': _('Suggest improvements to existing features'),
            'compliment': _('Share positive feedback'),
            'complaint': _('Report dissatisfaction or concerns'),
            'question': _('Ask for help or clarification'),
            'other': _('Any other type of feedback')
        }

        return context


@method_decorator(login_required, name='dispatch')
class FeedbackDashboardView(View):
    """Vue principale du dashboard feedback"""

    def get(self, request):
        user_feedbacks = UserFeedback.objects.filter(user=request.user)

        # Statistiques générales
        stats = {
            'total': user_feedbacks.count(),
            'new': user_feedbacks.filter(status='new').count(),
            'in_progress': user_feedbacks.filter(status='in_progress').count(),
            'resolved': user_feedbacks.filter(status='resolved').count(),
            'closed': user_feedbacks.filter(status='closed').count(),
        }

        # Filtrage
        filtered_feedbacks = user_feedbacks

        # Filtrage par statut
        status_filter = request.GET.get('status')
        if status_filter:
            filtered_feedbacks = filtered_feedbacks.filter(status=status_filter)

        # Filtrage par type
        type_filter = request.GET.get('type')
        if type_filter:
            filtered_feedbacks = filtered_feedbacks.filter(feedback_type=type_filter)

        # Recherche
        search = request.GET.get('search')
        if search:
            filtered_feedbacks = filtered_feedbacks.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # Tous les feedbacks
        recent_feedbacks = filtered_feedbacks.select_related(
            'assigned_to'
        ).prefetch_related(
            'responses', 'attachments'
        ).order_by('-created_at')

        # Distribution par type
        type_distribution = {}
        for choice_key, choice_label in FEEDBACK_TYPE_CHOICES:
            count = user_feedbacks.filter(feedback_type=choice_key).count()
            if count > 0:
                type_distribution[choice_label] = count

        # Feedbacks en attente de réponse
        pending_feedbacks = user_feedbacks.filter(
            status__in=['new', 'in_progress']
        ).count()

        context = {
            'stats': stats,
            'recent_feedbacks': recent_feedbacks,
            'type_distribution': type_distribution,
            'pending_feedbacks': pending_feedbacks,
            'page_title': _('Bugs & Feedbacks'),
        }

        return render(request, 'authentication/feedback/feedback_dashboard.html', context)


@login_required
def ajax_feedback_status(request, pk):
    """API AJAX pour obtenir le statut d'un feedback"""
    try:
        feedback = get_object_or_404(
            UserFeedback,
            pk=pk,
            user=request.user
        )

        data = {
            'status': feedback.status,
            'status_display': feedback.get_status_display(),
            'status_color': feedback.get_status_display_with_color()['color'],
            'assigned_to': feedback.assigned_to.get_full_name() if feedback.assigned_to else None,
            'responses_count': feedback.responses.filter(is_internal=False).count(),
            'updated_at': feedback.updated_at.strftime('%Y-%m-%d %H:%M') if feedback.updated_at else None,
        }

        return JsonResponse(data)

    except Exception as e:
        logger.error(f"Error getting feedback status: {e}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def ajax_mark_feedback_seen(request, pk):
    """Marquer un feedback comme vu par l'utilisateur"""
    if request.method == 'POST':
        try:
            feedback = get_object_or_404(
                UserFeedback,
                pk=pk,
                user=request.user
            )

            # Ici on pourrait ajouter un champ "last_seen_by_user" si nécessaire
            # Pour l'instant, on met juste à jour updated_at
            feedback.save(update_fields=['updated_at'])

            return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Error marking feedback as seen: {e}")
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


