"""
Course management views following OpenEdX patterns.
Handles course creation, editing, and content management.
"""
import json
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib import messages

from apps.teachers.models import Teacher
from ..models import CMSUnit
from ..models import CourseSettings, CourseContent
from ..utils.access import has_course_write_access


class CourseStudioView(View):
    """
    Main course studio view following OpenEdX Studio patterns.
    Provides the main interface for course editing.
    """
    
    @method_decorator(login_required)
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, course_id):
        """Render the main course studio interface."""
        try:
            # Get course and verify access
            course = get_object_or_404(CMSUnit, pk=course_id)
            teacher = get_object_or_404(Teacher, user=request.user)
            
            if course.teacher != teacher:
                raise Http404("Course not found or access denied")
            
            # Get course settings
            course_settings, _ = CourseSettings.objects.get_or_create(
                course_id=str(course.id),
                defaults={
                    'display_name': course.title,
                    'short_description': course.description or '',
                    'language': 'fr',
                }
            )
            
            context = {
                'course': course,
                'course_settings': course_settings,
                'course_id': course.id,
                'user': request.user,
                'teacher': teacher,
            }
            
            from django.shortcuts import render
            return render(request, 'contentstore/course_studio.html', context)
            
        except Exception as e:
            raise Http404(f"Error loading course studio: {str(e)}")


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
@login_required
@ensure_csrf_cookie
def course_handler(request, course_id=None):
    """
    RESTful course handler following OpenEdX patterns.
    Handles CRUD operations for courses.
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    
    if request.method == 'GET':
        if course_id:
            # Get specific course
            course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
            return JsonResponse({
                'success': True,
                'course': {
                    'id': course.id,
                    'display_name': course.title,
                    'description': course.description,
                    'level': course.level,
                    'price': float(course.price),
                    'is_published': course.is_published,
                    'sync_status': course.sync_status,
                    'created_at': course.created_at.isoformat(),
                    'updated_at': course.updated_at.isoformat(),
                }
            })
        else:
            # List all courses for teacher
            courses = CMSUnit.objects.filter(teacher=teacher)
            courses_data = []
            for course in courses:
                courses_data.append({
                    'id': course.id,
                    'display_name': course.title,
                    'description': course.description,
                    'level': course.level,
                    'is_published': course.is_published,
                    'sync_status': course.sync_status,
                    'chapters_count': course.chapters.count(),
                    'lessons_count': course.lessons.count(),
                })
            
            return JsonResponse({
                'success': True,
                'courses': courses_data,
                'total_count': len(courses_data)
            })
    
    elif request.method == 'POST':
        # Create new course
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['title_fr', 'title_en', 'title_es', 'title_nl', 'level']
            for field in required_fields:
                if field not in data or not data[field].strip():
                    return JsonResponse({
                        'success': False,
                        'error': f'Field {field} is required'
                    }, status=400)
            
            # Create course
            course = CMSUnit.objects.create(
                teacher=teacher,
                title_en=data['title_en'],
                title_fr=data['title_fr'],
                title_es=data['title_es'],
                title_nl=data['title_nl'],
                description_en=data.get('description_en', ''),
                description_fr=data.get('description_fr', ''),
                description_es=data.get('description_es', ''),
                description_nl=data.get('description_nl', ''),
                level=data['level'],
                price=data.get('price', 0),
                order=CMSUnit.objects.filter(teacher=teacher).count() + 1
            )
            
            # Create course settings
            CourseSettings.objects.create(
                course_id=str(course.id),
                display_name=course.title,
                short_description=course.description or '',
                language='fr',
            )
            
            return JsonResponse({
                'success': True,
                'course_id': course.id,
                'message': 'Course created successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'PUT':
        # Update existing course
        if not course_id:
            return JsonResponse({
                'success': False,
                'error': 'Course ID required for update'
            }, status=400)
        
        course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
        
        try:
            data = json.loads(request.body)
            
            # Update course fields
            for field in ['title_en', 'title_fr', 'title_es', 'title_nl',
                         'description_en', 'description_fr', 'description_es', 'description_nl',
                         'level', 'price', 'is_published']:
                if field in data:
                    setattr(course, field, data[field])
            
            course.save()
            
            # Update course settings if they exist
            try:
                course_settings = CourseSettings.objects.get(course_id=str(course.id))
                course_settings.display_name = course.title
                course_settings.short_description = course.description or ''
                course_settings.save()
            except CourseSettings.DoesNotExist:
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Course updated successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'DELETE':
        # Delete course
        if not course_id:
            return JsonResponse({
                'success': False,
                'error': 'Course ID required for deletion'
            }, status=400)
        
        course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
        
        # Check if course can be deleted (not published or synced)
        if course.is_published and course.sync_status == 'synced':
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete published and synced course'
            }, status=400)
        
        try:
            course_title = course.title
            course.delete()
            
            # Delete associated course settings
            CourseSettings.objects.filter(course_id=str(course_id)).delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Course "{course_title}" deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@require_http_methods(["POST"])
@login_required
@ensure_csrf_cookie
def course_publish_handler(request, course_id):
    """
    Handler for publishing/unpublishing courses.
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')  # 'publish' or 'unpublish'
        
        if action not in ['publish', 'unpublish']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid action. Must be "publish" or "unpublish"'
            }, status=400)
        
        if action == 'publish':
            # For now, we'll allow publishing without content for testing
            # Validate course has basic information
            if course.price is None or course.price < 0:
                return JsonResponse({
                    'success': False,
                    'error': 'Le cours doit avoir un prix valide pour être publié'
                }, status=400)
            
            # Check if course has a description
            if not course.description_fr:
                return JsonResponse({
                    'success': False,
                    'error': 'Le cours doit avoir une description pour être publié'
                }, status=400)
            
            course.is_published = True
            course.sync_status = 'pending'  # Mark for sync to backend
            success_message = f'Cours "{course.title}" publié avec succès!'
            
        else:  # unpublish
            course.is_published = False
            course.sync_status = 'pending'  # Mark for sync to backend
            success_message = f'Cours "{course.title}" dépublié avec succès!'
        
        course.save()
        
        # Update course settings to reflect publication status
        try:
            course_settings = CourseSettings.objects.get(course_id=str(course.id))
            course_settings.published = course.is_published
            course_settings.save()
        except CourseSettings.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'message': success_message,
            'is_published': course.is_published,
            'sync_status': course.sync_status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET", "POST"])
@login_required
@ensure_csrf_cookie
def course_settings_handler(request, course_id):
    """
    Handler for course settings following OpenEdX patterns.
    """
    teacher = get_object_or_404(Teacher, user=request.user)
    course = get_object_or_404(CMSUnit, pk=course_id, teacher=teacher)
    
    if request.method == 'GET':
        # Get course settings
        course_settings, _ = CourseSettings.objects.get_or_create(
            course_id=str(course.id),
            defaults={
                'display_name': course.title,
                'short_description': course.description or '',
                'language': 'fr',
            }
        )
        
        return JsonResponse({
            'success': True,
            'settings': {
                'display_name': course_settings.display_name,
                'short_description': course_settings.short_description,
                'overview': course_settings.overview,
                'language': course_settings.language,
                'effort': course_settings.effort,
                'start_date': course_settings.start_date.isoformat() if course_settings.start_date else None,
                'end_date': course_settings.end_date.isoformat() if course_settings.end_date else None,
                'enrollment_start': course_settings.enrollment_start.isoformat() if course_settings.enrollment_start else None,
                'enrollment_end': course_settings.enrollment_end.isoformat() if course_settings.enrollment_end else None,
                'advanced_settings': course_settings.advanced_settings,
                'grading_policy': course_settings.grading_policy,
            }
        })
    
    elif request.method == 'POST':
        # Update course settings
        try:
            data = json.loads(request.body)
            
            course_settings, _ = CourseSettings.objects.get_or_create(
                course_id=str(course.id),
                defaults={
                    'display_name': course.title,
                    'short_description': course.description or '',
                    'language': 'fr',
                }
            )
            
            # Update settings fields
            for field in ['display_name', 'short_description', 'overview', 'language', 'effort']:
                if field in data:
                    setattr(course_settings, field, data[field])
            
            # Handle date fields
            from django.utils.dateparse import parse_datetime
            for date_field in ['start_date', 'end_date', 'enrollment_start', 'enrollment_end']:
                if date_field in data and data[date_field]:
                    try:
                        setattr(course_settings, date_field, parse_datetime(data[date_field]))
                    except ValueError:
                        pass
            
            # Handle JSON fields
            if 'advanced_settings' in data:
                course_settings.advanced_settings = data['advanced_settings']
            if 'grading_policy' in data:
                course_settings.grading_policy = data['grading_policy']
            
            course_settings.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Course settings updated successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)