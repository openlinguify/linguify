from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from .services import SyncManager
from apps.contentstore.models import CMSUnit
from apps.teachers.models import Teacher

class SyncStatusView(LoginRequiredMixin, View):
    """View sync status for teacher's content."""
    
    def get(self, request):
        teacher = get_object_or_404(Teacher, user=request.user)
        
        status = {
            'teacher_sync_status': teacher.sync_status,
            'units': {
                'total': teacher.units.count(),
                'synced': teacher.units.filter(sync_status='synced').count(),
                'pending': teacher.units.filter(sync_status='pending').count(),
                'failed': teacher.units.filter(sync_status='failed').count(),
            },
            'last_sync': teacher.last_sync.isoformat() if teacher.last_sync else None,
        }
        
        return JsonResponse(status)

class SyncAllView(LoginRequiredMixin, View):
    """Sync all pending content for a teacher."""
    
    def post(self, request):
        teacher = get_object_or_404(Teacher, user=request.user)
        sync_manager = SyncManager()
        
        # Mark teacher as pending if not already synced
        if teacher.sync_status != 'synced':
            teacher.mark_for_sync()
        
        # Mark all published units as pending
        for unit in teacher.units.filter(is_published=True):
            if unit.sync_status != 'synced':
                unit.mark_for_sync()
                
                # Mark chapters and lessons as pending
                for chapter in unit.chapters.all():
                    if chapter.sync_status != 'synced':
                        chapter.mark_for_sync()
                
                for lesson in unit.lessons.all():
                    if lesson.sync_status != 'synced':
                        lesson.mark_for_sync()
        
        # Perform sync
        results = sync_manager.sync_pending_content()
        
        return JsonResponse({
            'success': len(results['errors']) == 0,
            'results': results
        })

class SyncUnitView(LoginRequiredMixin, View):
    """Sync a specific unit with all its content."""
    
    def post(self, request, unit_id):
        teacher = get_object_or_404(Teacher, user=request.user)
        unit = get_object_or_404(CMSUnit, id=unit_id, teacher=teacher)
        
        if not unit.is_published:
            return JsonResponse({
                'success': False,
                'error': 'Unit must be published before sync'
            })
        
        sync_manager = SyncManager()
        results = sync_manager.sync_unit_with_content(unit)
        
        return JsonResponse(results)