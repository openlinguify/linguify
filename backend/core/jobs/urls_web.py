from django.urls import path
from . import views_web
from django.http import JsonResponse
from django.views import View

app_name = 'jobs_web'

class DebugJobsView(View):
    def get(self, request):
        try:
            from .models import JobPosition
            positions = JobPosition.objects.all()
            data = []
            for p in positions:
                data.append({
                    'id': p.id,
                    'title': p.title,
                    'is_active': p.is_active
                })
            
            return JsonResponse({
                'success': True,
                'positions': data,
                'count': len(data)
            })
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            })

urlpatterns = [
    # Debug endpoint
    path('debug/', DebugJobsView.as_view(), name='debug'),
    
    # Page principale des carrières
    path('', views_web.CareersView.as_view(), name='careers'),
    
    # Détail d'une position
    path('position/<int:position_id>/', views_web.CareersPositionDetailView.as_view(), name='position_detail'),
    
    # Candidature pour un poste
    path('apply/<int:position_id>/', views_web.JobApplicationView.as_view(), name='apply'),
]