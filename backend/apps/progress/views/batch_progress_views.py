# backend/progress/views/batch_progress_views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
import logging

from django.contrib.contenttypes.models import ContentType
from apps.course.models import ContentLesson, Lesson
from ..models.progress_course import UserCourseProgress, UserLessonProgress, UserUnitProgress

logger = logging.getLogger(__name__)

class BatchProgressUpdateView(APIView):
    """
    Endpoint for updating multiple progress items in a single API call.
    This reduces the number of API calls needed when tracking progress
    in activities like vocabulary lessons where progress updates happen frequently.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        
        # Get language code from request or user profile
        language_code = request.data.get('language_code') or request.query_params.get('language_code')
        if not language_code and user.is_authenticated:
            language_code = getattr(user, 'target_language', 'en')
        language_code = language_code.lower() if language_code else 'en'
        
        # Get batch updates from request data
        batch_updates = request.data.get('updates', [])
        if not isinstance(batch_updates, list):
            return Response({
                'error': 'Updates must be a list of progress items'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Track results for response
        results = {
            'successful_updates': 0,
            'failed_updates': 0,
            'details': []
        }
        
        # Process each update in the batch
        for update in batch_updates:
            try:
                update_type = update.get('type')
                object_id = update.get('object_id')
                completion_percentage = update.get('completion_percentage', 0)
                time_spent = update.get('time_spent', 0)
                xp_earned = update.get('xp_earned', 0)
                is_completed = update.get('is_completed', False)
                
                # Validate required fields
                if not update_type or not object_id:
                    results['failed_updates'] += 1
                    results['details'].append({
                        'error': 'Missing required fields: type or object_id',
                        'update': update
                    })
                    continue
                
                # Process based on update type
                if update_type == 'content_lesson':
                    self._update_content_lesson_progress(
                        user, object_id, language_code, completion_percentage, 
                        time_spent, xp_earned, is_completed, results
                    )
                    
                elif update_type == 'lesson':
                    parent_content_id = update.get('parent_content_id')
                    self._update_lesson_progress(
                        user, object_id, language_code, completion_percentage,
                        time_spent, is_completed, parent_content_id, results
                    )
                    
                elif update_type == 'unit':
                    self._update_unit_progress(
                        user, object_id, language_code, completion_percentage,
                        is_completed, results
                    )
                    
                else:
                    results['failed_updates'] += 1
                    results['details'].append({
                        'error': f'Invalid update type: {update_type}',
                        'update': update
                    })
            
            except Exception as e:
                logger.error(f"Error processing update: {str(e)}", exc_info=True)
                results['failed_updates'] += 1
                results['details'].append({
                    'error': str(e),
                    'update': update
                })
        
        # Log summary
        logger.info(f"Batch progress update completed: {results['successful_updates']} successful, {results['failed_updates']} failed")
        
        return Response({
            'success': True,
            'results': results
        }, status=status.HTTP_200_OK)
    
    def _update_content_lesson_progress(self, user, content_lesson_id, language_code, 
                                       completion_percentage, time_spent, xp_earned, 
                                       is_completed, results):
        """Update progress for a content lesson"""
        try:
            # Get the content lesson to ensure it exists
            content_lesson = ContentLesson.objects.get(id=content_lesson_id)
            
            # Get content type for ContentLesson model
            content_type = ContentType.objects.get_for_model(ContentLesson)
            
            # Get or create the progress record
            progress, created = UserCourseProgress.objects.get_or_create(
                user=user,
                content_type=content_type,
                object_id=content_lesson_id,
                language_code=language_code,
                defaults={
                    'status': 'not_started',
                    'completion_percentage': 0,
                    'xp_earned': 0,
                    'time_spent': 0
                }
            )
            
            # Update progress data
            progress.completion_percentage = max(progress.completion_percentage, completion_percentage)
            progress.time_spent = progress.time_spent + time_spent
            progress.xp_earned = max(progress.xp_earned, xp_earned)
            
            # Update status based on completion percentage and is_completed flag
            if is_completed or completion_percentage >= 100:
                progress.status = 'completed'
                progress.completed_at = timezone.now()
            elif progress.status == 'not_started' and (completion_percentage > 0 or time_spent > 0):
                progress.status = 'in_progress'
            
            progress.save()
            
            results['successful_updates'] += 1
            results['details'].append({
                'type': 'content_lesson',
                'id': content_lesson_id,
                'status': progress.status,
                'completion_percentage': progress.completion_percentage
            })
            
            return progress
        
        except ContentLesson.DoesNotExist:
            results['failed_updates'] += 1
            results['details'].append({
                'error': f'Content lesson with ID {content_lesson_id} does not exist',
                'type': 'content_lesson',
                'id': content_lesson_id
            })
            return None
        
        except Exception as e:
            results['failed_updates'] += 1
            results['details'].append({
                'error': str(e),
                'type': 'content_lesson',
                'id': content_lesson_id
            })
            return None
    
    def _update_lesson_progress(self, user, lesson_id, language_code, completion_percentage, 
                              time_spent, is_completed, parent_content_id, results):
        """Update progress for a lesson"""
        try:
            # Get the lesson to ensure it exists and to get its unit
            lesson = Lesson.objects.get(id=lesson_id)
            
            # Get or create the progress record
            progress, created = UserLessonProgress.objects.get_or_create(
                user=user,
                lesson=lesson,
                language_code=language_code,
                defaults={
                    'status': 'not_started',
                    'completion_percentage': 0,
                    'time_spent': 0
                }
            )
            
            # Update progress data
            progress.completion_percentage = max(progress.completion_percentage, completion_percentage)
            progress.time_spent = progress.time_spent + time_spent
            
            # Update status based on completion percentage and is_completed flag
            if is_completed or completion_percentage >= 100:
                progress.status = 'completed'
                progress.completed_at = timezone.now()
            elif progress.status == 'not_started' and (completion_percentage > 0 or time_spent > 0):
                progress.status = 'in_progress'
            
            progress.save()
            
            # If this was triggered by a content lesson completion, update unit progress too
            if completion_percentage >= 100 and lesson.unit:
                self._update_unit_progress_from_lessons(user, lesson.unit.id, language_code, results)
            
            results['successful_updates'] += 1
            results['details'].append({
                'type': 'lesson',
                'id': lesson_id,
                'status': progress.status,
                'completion_percentage': progress.completion_percentage
            })
            
            return progress
        
        except Lesson.DoesNotExist:
            results['failed_updates'] += 1
            results['details'].append({
                'error': f'Lesson with ID {lesson_id} does not exist',
                'type': 'lesson',
                'id': lesson_id
            })
            return None
        
        except Exception as e:
            results['failed_updates'] += 1
            results['details'].append({
                'error': str(e),
                'type': 'lesson',
                'id': lesson_id
            })
            return None
    
    def _update_unit_progress(self, user, unit_id, language_code, completion_percentage, 
                            is_completed, results):
        """Update progress for a unit directly"""
        try:
            # Get or create the progress record
            progress, created = UserUnitProgress.objects.get_or_create(
                user=user,
                unit_id=unit_id,
                language_code=language_code,
                defaults={
                    'status': 'not_started',
                    'completion_percentage': 0
                }
            )
            
            # Update progress data
            progress.completion_percentage = max(progress.completion_percentage, completion_percentage)
            
            # Update status based on completion percentage and is_completed flag
            if is_completed or completion_percentage >= 100:
                progress.status = 'completed'
                progress.completed_at = timezone.now()
            elif progress.status == 'not_started' and completion_percentage > 0:
                progress.status = 'in_progress'
            
            progress.save()
            
            results['successful_updates'] += 1
            results['details'].append({
                'type': 'unit',
                'id': unit_id,
                'status': progress.status,
                'completion_percentage': progress.completion_percentage
            })
            
            return progress
        
        except Exception as e:
            results['failed_updates'] += 1
            results['details'].append({
                'error': str(e),
                'type': 'unit',
                'id': unit_id
            })
            return None
    
    def _update_unit_progress_from_lessons(self, user, unit_id, language_code, results):
        """Calculate and update unit progress based on lesson completion"""
        try:
            # Get all lesson progress for this unit
            lesson_progresses = UserLessonProgress.objects.filter(
                user=user,
                lesson__unit_id=unit_id,
                language_code=language_code
            )
            
            # Get total number of lessons in the unit
            total_lessons = Lesson.objects.filter(unit_id=unit_id).count()
            
            if total_lessons == 0:
                return
            
            # Calculate completion percentage based on completed lessons
            completed_lessons = sum(1 for lp in lesson_progresses if lp.status == 'completed')
            completion_percentage = round((completed_lessons / total_lessons) * 100)
            
            # Update unit progress
            unit_progress, created = UserUnitProgress.objects.get_or_create(
                user=user,
                unit_id=unit_id,
                language_code=language_code,
                defaults={
                    'status': 'not_started',
                    'completion_percentage': 0
                }
            )
            
            unit_progress.completion_percentage = completion_percentage
            
            # Update status based on completion percentage
            if completion_percentage >= 100:
                unit_progress.status = 'completed'
                unit_progress.completed_at = timezone.now()
            elif completion_percentage > 0:
                unit_progress.status = 'in_progress'
            
            unit_progress.save()
            
            results['successful_updates'] += 1
            results['details'].append({
                'type': 'unit',
                'id': unit_id,
                'status': unit_progress.status,
                'completion_percentage': unit_progress.completion_percentage,
                'note': 'Updated from lesson progress'
            })
            
            return unit_progress
        
        except Exception as e:
            results['failed_updates'] += 1
            results['details'].append({
                'error': str(e),
                'type': 'unit',
                'id': unit_id,
                'note': 'Failed to update from lesson progress'
            })
            return None


class BatchProgressStatusView(APIView):
    """
    Endpoint for retrieving batch progress status for multiple items.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Get language code from request or user profile
        language_code = request.data.get('language_code') or request.query_params.get('language_code')
        if not language_code and user.is_authenticated:
            language_code = getattr(user, 'target_language', 'en')
        language_code = language_code.lower() if language_code else 'en'
        
        # Get items to check from request data
        items = request.data.get('items', [])
        if not isinstance(items, list):
            return Response({
                'error': 'Items must be a list of progress items to check'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        
        content_lesson_type = ContentType.objects.get_for_model(ContentLesson)
        
        for item in items:
            try:
                item_type = item.get('type')
                item_id = item.get('id')
                
                if not item_type or not item_id:
                    results.append({
                        'error': 'Missing required fields: type or id',
                        'item': item
                    })
                    continue
                
                if item_type == 'content_lesson':
                    progress = UserCourseProgress.objects.filter(
                        user=user,
                        content_type=content_lesson_type,
                        object_id=item_id,
                        language_code=language_code
                    ).first()
                    
                elif item_type == 'lesson':
                    progress = UserLessonProgress.objects.filter(
                        user=user,
                        lesson_id=item_id,
                        language_code=language_code
                    ).first()
                    
                elif item_type == 'unit':
                    progress = UserUnitProgress.objects.filter(
                        user=user,
                        unit_id=item_id,
                        language_code=language_code
                    ).first()
                    
                else:
                    results.append({
                        'error': f'Invalid item type: {item_type}',
                        'item': item
                    })
                    continue
                
                if progress:
                    results.append({
                        'type': item_type,
                        'id': item_id,
                        'status': progress.status,
                        'completion_percentage': progress.completion_percentage,
                        'time_spent': getattr(progress, 'time_spent', None),
                        'xp_earned': getattr(progress, 'xp_earned', None),
                        'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                    })
                else:
                    results.append({
                        'type': item_type,
                        'id': item_id,
                        'status': 'not_started',
                        'completion_percentage': 0,
                        'time_spent': 0,
                        'xp_earned': 0,
                        'completed_at': None,
                    })
                    
            except Exception as e:
                logger.error(f"Error checking progress status: {str(e)}", exc_info=True)
                results.append({
                    'error': str(e),
                    'item': item
                })
        
        return Response({
            'success': True,
            'language_code': language_code,
            'results': results
        }, status=status.HTTP_200_OK)