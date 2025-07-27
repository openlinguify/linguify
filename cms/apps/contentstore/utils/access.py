"""
Access control utilities following OpenEdX patterns.
Handles permissions and access control for course content.
"""
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.teachers.models import Teacher
from apps.contentstore.models import CMSUnit


def has_course_write_access(user, course_id):
    """
    Check if user has write access to a course.
    Following OpenEdX access control patterns.
    """
    if not user.is_authenticated:
        return False
    
    try:
        teacher = Teacher.objects.get(user=user)
        course = CMSUnit.objects.get(pk=course_id, teacher=teacher)
        return teacher.is_active
    except (Teacher.DoesNotExist, CMSUnit.DoesNotExist):
        return False


def has_course_read_access(user, course_id):
    """
    Check if user has read access to a course.
    For now, same as write access but can be extended.
    """
    return has_course_write_access(user, course_id)


def require_course_write_access(user, course_id):
    """
    Require write access to course, raise PermissionDenied if not allowed.
    """
    if not has_course_write_access(user, course_id):
        raise PermissionDenied("You do not have permission to modify this course.")


def require_course_read_access(user, course_id):
    """
    Require read access to course, raise PermissionDenied if not allowed.
    """
    if not has_course_read_access(user, course_id):
        raise PermissionDenied("You do not have permission to view this course.")


def get_user_courses(user):
    """
    Get all courses that user has access to.
    """
    if not user.is_authenticated:
        return CMSUnit.objects.none()
    
    try:
        teacher = Teacher.objects.get(user=user)
        return CMSUnit.objects.filter(teacher=teacher)
    except Teacher.DoesNotExist:
        return CMSUnit.objects.none()


def is_course_author(user, course_id):
    """
    Check if user is the original author of the course.
    """
    try:
        teacher = Teacher.objects.get(user=user)
        course = CMSUnit.objects.get(pk=course_id, teacher=teacher)
        return True
    except (Teacher.DoesNotExist, CMSUnit.DoesNotExist):
        return False


def can_delete_course(user, course_id):
    """
    Check if user can delete a course.
    Courses can only be deleted if they are not published or synced.
    """
    if not has_course_write_access(user, course_id):
        return False
    
    try:
        course = CMSUnit.objects.get(pk=course_id)
        # Cannot delete published and synced courses
        if course.is_published and course.sync_status == 'synced':
            return False
        return True
    except CMSUnit.DoesNotExist:
        return False


def can_publish_course(user, course_id):
    """
    Check if user can publish a course.
    """
    if not has_course_write_access(user, course_id):
        return False
    
    try:
        teacher = Teacher.objects.get(user=user)
        # Only approved teachers can publish courses
        return teacher.is_active
    except Teacher.DoesNotExist:
        return False