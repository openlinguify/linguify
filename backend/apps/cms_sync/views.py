"""
CMS Sync API endpoints to receive data from Teacher CMS.
"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone

from apps.course.models.core import Unit, Chapter, Lesson, ContentLesson
from apps.teaching.models import Teacher, TeacherLanguage, TeacherAvailability
from .serializers import (CMSUnitSerializer, CMSChapterSerializer, CMSLessonSerializer,
                         CMSTeacherSerializer)

@api_view(['POST', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sync_teacher(request):
    """Sync teacher data from CMS."""
    
    serializer = CMSTeacherSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    cms_teacher_id = serializer.validated_data['cms_teacher_id']
    
    # Get or create teacher
    teacher, created = Teacher.objects.get_or_create(
        cms_teacher_id=cms_teacher_id,
        defaults={
            'user_id': serializer.validated_data['user_id'],
            'full_name': serializer.validated_data['full_name'],
            'bio_en': serializer.validated_data.get('bio_en', ''),
            'bio_fr': serializer.validated_data.get('bio_fr', ''),
            'bio_es': serializer.validated_data.get('bio_es', ''),
            'bio_nl': serializer.validated_data.get('bio_nl', ''),
            'hourly_rate': serializer.validated_data['hourly_rate'],
            'years_experience': serializer.validated_data.get('years_experience', 0),
            'average_rating': serializer.validated_data.get('average_rating', 0),
            'total_hours_taught': serializer.validated_data.get('total_hours_taught', 0),
        }
    )
    
    if not created:
        # Update existing teacher
        for field, value in serializer.validated_data.items():
            if field != 'cms_teacher_id':
                setattr(teacher, field, value)
    
    teacher.last_sync = timezone.now()
    teacher.save()
    
    # Sync languages if provided
    languages_data = request.data.get('languages', [])
    if languages_data:
        # Clear existing languages
        teacher.teaching_languages.all().delete()
        
        for lang_data in languages_data:
            TeacherLanguage.objects.create(
                teacher=teacher,
                language_code=lang_data['language_code'],
                language_name=lang_data['language_name'],
                proficiency=lang_data['proficiency'],
                can_teach=lang_data.get('can_teach', True)
            )
    
    # Sync availability if provided
    availability_data = request.data.get('availability', [])
    if availability_data:
        # Clear existing availability
        teacher.availability_schedule.all().delete()
        
        for av_data in availability_data:
            TeacherAvailability.objects.create(
                teacher=teacher,
                day_of_week=av_data['day_of_week'],
                start_time=av_data['start_time'],
                end_time=av_data['end_time'],
                is_active=av_data.get('is_active', True)
            )
    
    return Response({
        'id': teacher.id,
        'cms_teacher_id': teacher.cms_teacher_id,
        'message': 'Teacher synced successfully'
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

@api_view(['POST', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sync_unit(request):
    """Sync unit/course data from CMS."""
    
    serializer = CMSUnitSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    cms_unit_id = request.data.get('cms_unit_id')
    teacher_cms_id = serializer.validated_data['teacher_cms_id']
    
    # Find teacher
    try:
        teacher = Teacher.objects.get(cms_teacher_id=teacher_cms_id)
    except Teacher.DoesNotExist:
        return Response(
            {'error': f'Teacher with CMS ID {teacher_cms_id} not found. Sync teacher first.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create unit
    if cms_unit_id:
        try:
            unit = Unit.objects.get(id=cms_unit_id)
            # Update existing
            for field, value in serializer.validated_data.items():
                if field != 'teacher_cms_id':
                    setattr(unit, field, value)
        except Unit.DoesNotExist:
            return Response(
                {'error': f'Unit with ID {cms_unit_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # Create new unit
        unit_data = serializer.validated_data.copy()
        unit_data.pop('teacher_cms_id', None)
        unit = Unit.objects.create(**unit_data)
    
    unit.save()
    
    return Response({
        'id': unit.id,
        'title': unit.title,
        'message': 'Unit synced successfully'
    }, status=status.HTTP_201_CREATED if not cms_unit_id else status.HTTP_200_OK)

@api_view(['POST', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sync_chapter(request):
    """Sync chapter data from CMS."""
    
    serializer = CMSChapterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    unit_id = serializer.validated_data['unit_id']
    cms_chapter_id = request.data.get('cms_chapter_id')
    
    # Find unit
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response(
            {'error': f'Unit with ID {unit_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get or create chapter
    if cms_chapter_id:
        try:
            chapter = Chapter.objects.get(id=cms_chapter_id)
            # Update existing
            for field, value in serializer.validated_data.items():
                setattr(chapter, field, value)
        except Chapter.DoesNotExist:
            return Response(
                {'error': f'Chapter with ID {cms_chapter_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # Create new chapter
        chapter = Chapter.objects.create(**serializer.validated_data)
    
    chapter.save()
    
    return Response({
        'id': chapter.id,
        'title': chapter.title,
        'message': 'Chapter synced successfully'
    }, status=status.HTTP_201_CREATED if not cms_chapter_id else status.HTTP_200_OK)

@api_view(['POST', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sync_lesson(request):
    """Sync lesson data from CMS."""
    
    serializer = CMSLessonSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    unit_id = serializer.validated_data['unit_id']
    chapter_id = serializer.validated_data.get('chapter_id')
    cms_lesson_id = request.data.get('cms_lesson_id')
    
    # Find unit
    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        return Response(
            {'error': f'Unit with ID {unit_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Find chapter if specified
    chapter = None
    if chapter_id:
        try:
            chapter = Chapter.objects.get(id=chapter_id, unit=unit)
        except Chapter.DoesNotExist:
            return Response(
                {'error': f'Chapter with ID {chapter_id} not found in unit {unit_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Get or create lesson
    if cms_lesson_id:
        try:
            lesson = Lesson.objects.get(id=cms_lesson_id)
            # Update existing
            for field, value in serializer.validated_data.items():
                setattr(lesson, field, value)
        except Lesson.DoesNotExist:
            return Response(
                {'error': f'Lesson with ID {cms_lesson_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # Create new lesson
        lesson_data = serializer.validated_data.copy()
        lesson_data['chapter'] = chapter
        lesson = Lesson.objects.create(**lesson_data)
    
    lesson.save()
    
    return Response({
        'id': lesson.id,
        'title': lesson.title,
        'message': 'Lesson synced successfully'
    }, status=status.HTTP_201_CREATED if not cms_lesson_id else status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def sync_status(request):
    """Get synchronization status."""
    
    stats = {
        'teachers': Teacher.objects.count(),
        'units': Unit.objects.count(),
        'chapters': Chapter.objects.count(),
        'lessons': Lesson.objects.count(),
        'last_sync': {
            'teachers': Teacher.objects.filter(
                last_sync__isnull=False
            ).order_by('-last_sync').first(),
            'units': Unit.objects.order_by('-updated_at').first(),
        }
    }
    
    # Format timestamps
    if stats['last_sync']['teachers']:
        stats['last_sync']['teachers'] = stats['last_sync']['teachers'].last_sync.isoformat()
    
    if stats['last_sync']['units']:
        stats['last_sync']['units'] = stats['last_sync']['units'].updated_at.isoformat()
    
    return Response(stats)

@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_synced_content(request):
    """Delete synced content (for testing purposes)."""
    
    content_type = request.data.get('content_type')
    cms_id = request.data.get('cms_id')
    
    if content_type == 'teacher' and cms_id:
        try:
            teacher = Teacher.objects.get(cms_teacher_id=cms_id)
            teacher.delete()
            return Response({'message': 'Teacher deleted successfully'})
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif content_type == 'unit' and cms_id:
        try:
            unit = Unit.objects.get(id=cms_id)
            unit.delete()
            return Response({'message': 'Unit deleted successfully'})
        except Unit.DoesNotExist:
            return Response({'error': 'Unit not found'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response(
            {'error': 'Invalid content_type or missing cms_id'},
            status=status.HTTP_400_BAD_REQUEST
        )