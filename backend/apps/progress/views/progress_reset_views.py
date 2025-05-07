from django.http import JsonResponse
from django.db import transaction, models
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.progress.models.progress_course import (
    UserUnitProgress,
    UserLessonProgress,
    UserContentLessonProgress,
    UserCourseProgress
)
from apps.course.models import Unit
from django.db.models import Q


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_all_progress(request):
    """
    Reset all progress data for the current user.
    """
    user = request.user
    
    try:
        # Try to get the target language from the user profile
        target_language = None
        try:
            from apps.authentication.models import User
            user_obj = User.objects.get(id=user.id)
            if hasattr(user_obj, 'target_language'):
                target_language = user_obj.target_language
                print(f"Found user target language: {target_language}")
        except Exception as user_error:
            print(f"Error getting user target language: {str(user_error)}")
        
        # If we found a target language, use the language-specific reset
        if target_language:
            return reset_progress_by_language(request)
        
        # Otherwise, perform a full reset of all progress
        with transaction.atomic():
            print(f"Performing full progress reset for user {user.id}")
            
            # First, get all progress IDs before deleting (for logging/debugging)
            content_count = UserContentLessonProgress.objects.filter(user=user).count()
            lesson_count = UserLessonProgress.objects.filter(user=user).count()
            unit_count = UserUnitProgress.objects.filter(user=user).count()
            course_count = UserCourseProgress.objects.filter(user=user).count()
            
            print(f"Found progress entries to reset: {content_count} contents, {lesson_count} lessons, {unit_count} units, {course_count} courses")
            
            # Delete all progress records for this user
            UserContentLessonProgress.objects.filter(user=user).delete()
            UserLessonProgress.objects.filter(user=user).delete()
            UserUnitProgress.objects.filter(user=user).delete()
            UserCourseProgress.objects.filter(user=user).delete()
            
            # Option: Create placeholder "not_started" entries for all available content
            # This ensures the user has an entry for each content item, but with 0 progress
            from apps.course.models import Lesson, Unit, ContentLesson
            
            # Get all content
            all_units = Unit.objects.all()
            all_lessons = Lesson.objects.all()
            all_contents = ContentLesson.objects.all()
            
            print(f"Creating placeholder entries for: {all_units.count()} units, {all_lessons.count()} lessons, {all_contents.count()} contents")
            
            # Create placeholder entries (optional - can be commented out if not needed)
            # Limit to a reasonable number to avoid performance issues
            max_entries = 50  # Adjust based on your needs
            
            for unit in all_units[:max_entries]:
                UserUnitProgress.objects.create(
                    user=user,
                    unit=unit,
                    status='not_started',
                    completion_percentage=0,
                    score=0,
                    time_spent=0
                )
                
            for lesson in all_lessons[:max_entries]:
                UserLessonProgress.objects.create(
                    user=user,
                    lesson=lesson,
                    status='not_started',
                    completion_percentage=0,
                    score=0,
                    time_spent=0
                )
                
            # Content lessons can be too many, so we'll skip those placeholders
            
            # You could optionally re-initialize progress if needed
            # But leaving it empty is often better for a true reset
        
        return JsonResponse({
            'success': True,
            'message': 'All progress has been reset successfully'
        })
    except Exception as e:
        print(f"Error in reset_all_progress: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error resetting progress: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_progress_by_language(request):
    """
    Reset progress data for a specific language for the current user.
    Expected query parameter: target_language
    """
    user = request.user
    target_language = request.GET.get('target_language')
    
    if not target_language:
        return JsonResponse({
            'success': False,
            'message': 'Target language is required'
        }, status=400)
    
    try:
        # Import models locally to avoid circular imports
        from apps.course.models import Lesson, ContentLesson
        
        # We'll use a comprehensive approach to ensure ALL progress for this language is reset:
        # 1. Identify all content by language
        # 2. Reset progress by language_code (main approach)
        # 3. Reset progress by specific content IDs (safety net)
        
        # First, try to identify all language-specific content
        # This will help us ensure we reset EVERYTHING related to this language
        
        # Get units that might be related to this language
        units = Unit.objects.all()
        
        # Try to find units by naming convention (title might contain language code)
        if target_language:
            lang_specific_units = units.filter(
                models.Q(title_en__icontains=target_language) | 
                models.Q(title_fr__icontains=target_language) |
                models.Q(title_es__icontains=target_language) |
                models.Q(title_nl__icontains=target_language)
            )
            if lang_specific_units.exists():
                print(f"Found {lang_specific_units.count()} units with language in title")
                units = lang_specific_units
        
        unit_ids = list(units.values_list('id', flat=True))
        
        # Logging for debugging
        print(f"Found {len(unit_ids)} units for language {target_language}")
        
        # Get lessons related to these units
        lessons = Lesson.objects.filter(unit__in=unit_ids)
        lesson_ids = list(lessons.values_list('id', flat=True))
        
        # Logging for debugging
        print(f"Found {len(lesson_ids)} lessons for units {unit_ids}")
        
        # Get content lessons related to these lessons
        content_lessons = ContentLesson.objects.filter(lesson__in=lesson_ids)
        content_lesson_ids = list(content_lessons.values_list('id', flat=True))
        
        # Logging for debugging
        print(f"Found {len(content_lesson_ids)} content lessons")
        
        with transaction.atomic():
            # APPROACH 1: Reset by language code (this should work based on the model definition)
            print(f"Resetting progress for user {user.id} with language_code={target_language}")
            
            # Option 1: Delete all progress with the specified language_code
            # This is the most direct approach
            deleted_contents = UserContentLessonProgress.objects.filter(user=user, language_code=target_language).delete()
            deleted_lessons = UserLessonProgress.objects.filter(user=user, language_code=target_language).delete()
            deleted_units = UserUnitProgress.objects.filter(user=user, language_code=target_language).delete()
            deleted_courses = UserCourseProgress.objects.filter(user=user, language_code=target_language).delete()
            
            print(f"Deleted items by language_code: {deleted_contents}, {deleted_lessons}, {deleted_units}, {deleted_courses}")
            
            # APPROACH 2: Reset by specific content IDs (safety net)
            print(f"Backup reset for content IDs: {len(content_lesson_ids)} contents, {len(lesson_ids)} lessons")
            
            if content_lesson_ids:
                # Option 1: Delete
                deleted = UserContentLessonProgress.objects.filter(
                    user=user,
                    content_lesson_id__in=content_lesson_ids
                ).delete()
                print(f"Deleted content progress: {deleted}")
                
                # Option 2: Reset to not_started (create or update entries)
                # This ensures we maintain the relationship but reset progress
                for content_id in content_lesson_ids:
                    UserContentLessonProgress.objects.update_or_create(
                        user=user,
                        content_lesson_id=content_id,
                        defaults={
                            'status': 'not_started',
                            'completion_percentage': 0,
                            'score': 0,
                            'time_spent': 0,
                            'completed_at': None,
                            'language_code': target_language,
                            'last_accessed': timezone.now()
                        }
                    )
            
            if lesson_ids:
                # Similar approach for lessons
                deleted = UserLessonProgress.objects.filter(
                    user=user,
                    lesson_id__in=lesson_ids
                ).delete()
                print(f"Deleted lesson progress: {deleted}")
                
                # Create fresh not_started entries
                for lesson_id in lesson_ids:
                    UserLessonProgress.objects.update_or_create(
                        user=user,
                        lesson_id=lesson_id,
                        defaults={
                            'status': 'not_started',
                            'completion_percentage': 0,
                            'score': 0,
                            'time_spent': 0,
                            'completed_at': None,
                            'language_code': target_language,
                            'last_accessed': timezone.now()
                        }
                    )
            
            if unit_ids:
                # Similar approach for units
                deleted = UserUnitProgress.objects.filter(
                    user=user,
                    unit_id__in=unit_ids
                ).delete()
                print(f"Deleted unit progress: {deleted}")
                
                # Create fresh not_started entries
                for unit_id in unit_ids:
                    UserUnitProgress.objects.update_or_create(
                        user=user,
                        unit_id=unit_id,
                        defaults={
                            'status': 'not_started',
                            'completion_percentage': 0,
                            'score': 0,
                            'time_spent': 0,
                            'completed_at': None,
                            'language_code': target_language,
                            'last_accessed': timezone.now()
                        }
                    )
        
        return JsonResponse({
            'success': True,
            'message': f'Progress for language {target_language} has been reset successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error resetting progress: {str(e)}'
        }, status=500)