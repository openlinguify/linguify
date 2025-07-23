"""
Synchronization services for CMS to Backend communication.
"""
import requests
import logging
from django.conf import settings
from apps.course_builder.models import CMSUnit, CMSChapter, CMSLesson, CMSContentLesson
from apps.teachers.models import Teacher

logger = logging.getLogger(__name__)

class BackendSyncService:
    """Service to sync CMS content to Backend API."""
    
    def __init__(self):
        self.base_url = settings.BACKEND_API_URL
        self.headers = {
            'Authorization': f'Token {settings.BACKEND_API_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    def sync_unit(self, cms_unit):
        """Sync a CMS unit to backend."""
        try:
            data = {
                'title_en': cms_unit.title_en,
                'title_fr': cms_unit.title_fr,
                'title_es': cms_unit.title_es,
                'title_nl': cms_unit.title_nl,
                'description_en': cms_unit.description_en,
                'description_fr': cms_unit.description_fr,
                'description_es': cms_unit.description_es,
                'description_nl': cms_unit.description_nl,
                'level': cms_unit.level,
                'order': cms_unit.order,
                'teacher_backend_id': cms_unit.teacher.backend_id,
            }
            
            if cms_unit.backend_id:
                # Update existing unit
                response = requests.put(
                    f"{self.base_url}course/units/{cms_unit.backend_id}/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            else:
                # Create new unit
                response = requests.post(
                    f"{self.base_url}course/units/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                backend_unit = response.json()
                cms_unit.mark_synced(backend_unit['id'])
                logger.info(f"Unit {cms_unit.id} synced successfully")
                return True
            else:
                error_msg = f"Backend API error: {response.status_code} - {response.text}"
                cms_unit.mark_sync_failed(error_msg)
                logger.error(f"Failed to sync unit {cms_unit.id}: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            cms_unit.mark_sync_failed(error_msg)
            logger.error(f"Failed to sync unit {cms_unit.id}: {error_msg}")
            return False
    
    def sync_chapter(self, cms_chapter):
        """Sync a CMS chapter to backend."""
        try:
            data = {
                'unit_backend_id': cms_chapter.unit.backend_id,
                'title_en': cms_chapter.title_en,
                'title_fr': cms_chapter.title_fr,
                'title_es': cms_chapter.title_es,
                'title_nl': cms_chapter.title_nl,
                'description_en': cms_chapter.description_en,
                'description_fr': cms_chapter.description_fr,
                'description_es': cms_chapter.description_es,
                'description_nl': cms_chapter.description_nl,
                'theme': cms_chapter.theme,
                'order': cms_chapter.order,
                'style': cms_chapter.style,
                'points_reward': cms_chapter.points_reward,
            }
            
            if cms_chapter.backend_id:
                response = requests.put(
                    f"{self.base_url}course/chapters/{cms_chapter.backend_id}/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{self.base_url}course/chapters/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                backend_chapter = response.json()
                cms_chapter.mark_synced(backend_chapter['id'])
                return True
            else:
                error_msg = f"Backend API error: {response.status_code} - {response.text}"
                cms_chapter.mark_sync_failed(error_msg)
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            cms_chapter.mark_sync_failed(error_msg)
            return False
    
    def sync_lesson(self, cms_lesson):
        """Sync a CMS lesson to backend."""
        try:
            data = {
                'unit_backend_id': cms_lesson.unit.backend_id,
                'chapter_backend_id': cms_lesson.chapter.backend_id if cms_lesson.chapter else None,
                'title_en': cms_lesson.title_en,
                'title_fr': cms_lesson.title_fr,
                'title_es': cms_lesson.title_es,
                'title_nl': cms_lesson.title_nl,
                'description_en': cms_lesson.description_en,
                'description_fr': cms_lesson.description_fr,
                'description_es': cms_lesson.description_es,
                'description_nl': cms_lesson.description_nl,
                'lesson_type': cms_lesson.lesson_type,
                'estimated_duration': cms_lesson.estimated_duration,
                'order': cms_lesson.order,
            }
            
            if cms_lesson.backend_id:
                response = requests.put(
                    f"{self.base_url}course/lessons/{cms_lesson.backend_id}/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{self.base_url}course/lessons/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                backend_lesson = response.json()
                cms_lesson.mark_synced(backend_lesson['id'])
                return True
            else:
                error_msg = f"Backend API error: {response.status_code} - {response.text}"
                cms_lesson.mark_sync_failed(error_msg)
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            cms_lesson.mark_sync_failed(error_msg)
            return False
    
    def sync_teacher(self, teacher):
        """Sync teacher profile to backend."""
        try:
            data = {
                'user_id': teacher.user.id,
                'full_name': teacher.full_name,
                'bio_en': teacher.bio_en,
                'bio_fr': teacher.bio_fr,
                'bio_es': teacher.bio_es,
                'bio_nl': teacher.bio_nl,
                'hourly_rate': float(teacher.hourly_rate),
                'years_experience': teacher.years_experience,
                'average_rating': float(teacher.average_rating),
                'total_hours_taught': teacher.total_hours_taught,
            }
            
            if teacher.backend_id:
                response = requests.put(
                    f"{self.base_url}teachers/{teacher.backend_id}/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{self.base_url}teachers/",
                    json=data,
                    headers=self.headers,
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                backend_teacher = response.json()
                teacher.mark_synced(backend_teacher['id'])
                return True
            else:
                error_msg = f"Backend API error: {response.status_code} - {response.text}"
                teacher.mark_sync_failed(error_msg)
                return False
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            teacher.mark_sync_failed(error_msg)
            return False

class SyncManager:
    """Manager to handle bulk synchronization."""
    
    def __init__(self):
        self.sync_service = BackendSyncService()
    
    def sync_pending_content(self):
        """Sync all content marked as pending."""
        results = {
            'teachers_synced': 0,
            'units_synced': 0,
            'chapters_synced': 0,
            'lessons_synced': 0,
            'errors': []
        }
        
        # Sync teachers first
        pending_teachers = Teacher.objects.filter(sync_status='pending')
        for teacher in pending_teachers:
            if self.sync_service.sync_teacher(teacher):
                results['teachers_synced'] += 1
            else:
                results['errors'].append(f"Teacher {teacher.id}: {teacher.sync_error}")
        
        # Sync units
        pending_units = CMSUnit.objects.filter(sync_status='pending', is_published=True)
        for unit in pending_units:
            if self.sync_service.sync_unit(unit):
                results['units_synced'] += 1
            else:
                results['errors'].append(f"Unit {unit.id}: {unit.sync_error}")
        
        # Sync chapters
        pending_chapters = CMSChapter.objects.filter(sync_status='pending', unit__is_published=True)
        for chapter in pending_chapters:
            if self.sync_service.sync_chapter(chapter):
                results['chapters_synced'] += 1
            else:
                results['errors'].append(f"Chapter {chapter.id}: {chapter.sync_error}")
        
        # Sync lessons
        pending_lessons = CMSLesson.objects.filter(sync_status='pending', unit__is_published=True)
        for lesson in pending_lessons:
            if self.sync_service.sync_lesson(lesson):
                results['lessons_synced'] += 1
            else:
                results['errors'].append(f"Lesson {lesson.id}: {lesson.sync_error}")
        
        return results
    
    def sync_unit_with_content(self, unit):
        """Sync a unit with all its content."""
        results = {'success': True, 'errors': []}
        
        # Sync unit first
        if not self.sync_service.sync_unit(unit):
            results['success'] = False
            results['errors'].append(f"Unit sync failed: {unit.sync_error}")
            return results
        
        # Sync chapters
        for chapter in unit.chapters.all():
            if not self.sync_service.sync_chapter(chapter):
                results['success'] = False
                results['errors'].append(f"Chapter {chapter.id} sync failed: {chapter.sync_error}")
        
        # Sync lessons
        for lesson in unit.lessons.all():
            if not self.sync_service.sync_lesson(lesson):
                results['success'] = False
                results['errors'].append(f"Lesson {lesson.id} sync failed: {lesson.sync_error}")
        
        return results