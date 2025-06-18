from django.shortcuts import render, get_object_or_404
from django.views import View
from django.utils.translation import gettext as _
from django.http import Http404
from .models import JobPosition, Department


class CareersView(View):
    """Page principale des carrières affichant tous les postes ouverts"""
    def get(self, request):
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