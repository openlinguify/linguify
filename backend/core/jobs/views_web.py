from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.db import IntegrityError
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.core.cache import cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.template.loader import get_template
from django.conf import settings
from .models import JobPosition, Department, JobApplication
from .forms import JobApplicationForm
import json
import logging

logger = logging.getLogger(__name__)


def send_application_confirmation_email(application):
    """Send confirmation email to the applicant"""
    try:
        # Render email templates
        html_template = get_template('jobs/emails/application_confirmation.html')
        text_template = get_template('jobs/emails/application_confirmation.txt')
        
        context = {
            'application': application,
        }
        
        html_content = html_template.render(context)
        text_content = text_template.render(context)
        
        # Send email
        subject = f'Application Confirmation - {application.position.title} at Open Linguify'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'careers@openlinguify.com')
        recipient_list = [application.email]
        
        send_mail(
            subject=subject,
            message=text_content,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_content,
            fail_silently=False
        )
        
        logger.info(f'Confirmation email sent to {application.email} for application #{application.id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send confirmation email to {application.email}: {str(e)}')
        return False


class CareersView(View):
    """Page principale des carrières affichant tous les postes ouverts"""
    def get(self, request):
        try:
            # Récupérer tous les postes ouverts groupés par département
            departments = Department.objects.filter(
                positions__is_active=True
            ).distinct().prefetch_related('positions')
            
            open_positions = JobPosition.objects.filter(is_active=True).select_related('department')
            
            context = {
                'title': _('Careers - Open Linguify'),
                'meta_description': _('Join our team at Open Linguify. Discover our open positions and help us revolutionize language learning.'),
                'departments': departments,
                'positions': open_positions,
                'total_positions': open_positions.count(),
            }
            return render(request, 'jobs/careers.html', context)
            
        except Exception as e:
            logger.error(f'Error in CareersView: {str(e)}')
            # Fallback context in case of database issues
            context = {
                'title': _('Careers - Open Linguify'),
                'meta_description': _('Join our team at Open Linguify. Discover our open positions and help us revolutionize language learning.'),
                'departments': [],
                'positions': [],
                'total_positions': 0,
                'error_message': _('We are currently updating our career opportunities. Please check back soon.'),
            }
            return render(request, 'jobs/careers.html', context)


class CareersPositionDetailView(View):
    """Page de détail d'un poste spécifique"""
    def get(self, request, position_id):
        try:
            position = get_object_or_404(JobPosition, id=position_id)
            
            # Vérifier si le poste est actif
            if not position.is_active:
                context = {
                    'title': _('Position Closed - Open Linguify'),
                    'position': position,
                }
                return render(request, 'jobs/careers_position_closed.html', context)
            
            # Récupérer d'autres postes similaires (même département)
            related_positions = JobPosition.objects.filter(
                department=position.department,
                is_active=True
            ).exclude(id=position.id)[:3]
            
            context = {
                'title': f'{position.title} - Careers - Open Linguify',
                'meta_description': f'Apply for {position.title} position at Open Linguify. {position.summary[:150]}...' if len(position.summary) > 150 else position.summary,
                'position': position,
                'related_positions': related_positions,
            }
            return render(request, 'jobs/careers_position_detail.html', context)
            
        except JobPosition.DoesNotExist:
            context = {
                'title': _('Position Not Found - Open Linguify'),
                'position_id': position_id,
            }
            return render(request, 'jobs/careers_position_not_found.html', context)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class JobApplicationView(View):
    """Vue pour traiter les candidatures à un poste avec CSRF protection"""
    
    def post(self, request, position_id):
        try:
            position = get_object_or_404(JobPosition, id=position_id, is_active=True)
        except JobPosition.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': _('Le poste demandé n\'existe pas ou n\'est plus disponible.')
            }, status=404)
        
        form = JobApplicationForm(request.POST, request.FILES, position=position)
        
        if form.is_valid():
            try:
                application = form.save()
                
                # Send confirmation email
                email_sent = send_application_confirmation_email(application)
                
                # Prepare success message
                if email_sent:
                    message = _('Votre candidature a été envoyée avec succès! Un email de confirmation a été envoyé à votre adresse.')
                else:
                    message = _('Votre candidature a été envoyée avec succès! Nous vous contacterons bientôt.')
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'application_id': application.id,
                    'email_sent': email_sent
                })
            except IntegrityError:
                # Duplicate application (same email for same position)
                return JsonResponse({
                    'success': False,
                    'error': _('Vous avez déjà postulé pour ce poste avec cette adresse email.')
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': _('Une erreur s\'est produite lors de l\'envoi de votre candidature. Veuillez réessayer.')
                })
        else:
            # Form validation errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = field_errors[0] if field_errors else ''
            
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': _('Veuillez corriger les erreurs dans le formulaire.')
            })

    def get(self, request, position_id):
        """Retourner le formulaire de candidature pour un poste avec gestion d'erreur robuste"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f'JobApplicationView.get called for position_id={position_id}')
        
        try:
            # Debug: Log tous les postes disponibles
            all_positions = JobPosition.objects.all()
            logger.info(f'Available positions: {[(p.id, p.title, p.is_active) for p in all_positions]}')
            
            # Vérifier d'abord si le poste existe
            position = JobPosition.objects.filter(id=position_id, is_active=True).first()
            logger.info(f'Position found: {position}')
            
            if not position:
                logger.warning(f'Position {position_id} not found or inactive')
                return JsonResponse({
                    'success': False,
                    'error': _('Le poste demandé n\'existe pas ou n\'est plus disponible.'),
                    'code': 'POSITION_NOT_FOUND'
                }, status=404)
            
            # Vérifier le cache avec la langue actuelle
            current_language = getattr(request, 'LANGUAGE_CODE', 'fr')
            cache_key = f'job_application_form_{position_id}_{current_language}'
            cached_form = cache.get(cache_key)
            
            if cached_form and not request.GET.get('nocache'):
                return JsonResponse({
                    'success': True,
                    'html': cached_form,
                    'position_title': position.title,
                    'cached': True
                })
            
            # Créer le formulaire
            form = JobApplicationForm(position=position)
            
            context = {
                'form': form,
                'position': position,
                'csrf_token': request.META.get('CSRF_COOKIE', ''),
            }
            
            # Render le template avec gestion d'erreur
            try:
                html_content = render_to_string('jobs/application_form.html', context, request=request)
            except Exception as template_error:
                return JsonResponse({
                    'success': False,
                    'error': _('Erreur lors du rendu du formulaire.'),
                    'code': 'TEMPLATE_ERROR',
                    'debug': str(template_error) if request.user.is_staff else None
                }, status=500)
            
            # Cache avec une durée plus courte pour les formulaires avec CSRF
            cache.set(cache_key, html_content, 180)  # Cache pendant 3 minutes
            
            return JsonResponse({
                'success': True,
                'html': html_content,
                'position_title': position.title,
                'cached': False,
                'csrf_token': request.META.get('CSRF_COOKIE', '')
            })
            
        except Exception as e:
            # Log l'erreur pour le débogage
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error in JobApplicationView.get for position {position_id}: {e}', exc_info=True)
            
            return JsonResponse({
                'success': False,
                'error': _('Une erreur inattendue s\'est produite.'),
                'code': 'UNEXPECTED_ERROR',
                'debug': str(e) if request.user.is_staff else None
            }, status=500)