# backend/progress/views.py

from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from course.models import Unit, Lesson, ContentLesson
from ..models.progress_course import (
    UserCourseProgress, 
    UserLessonProgress, 
    UserUnitProgress,
    UserContentLessonProgress
)
from ..serializers.progress_course_serializers import (
    UserLessonProgressSerializer,
    UserUnitProgressSerializer,
    ContentLessonProgressSerializer,
    UserCourseContentProgressSerializer,
    LessonProgressUpdateSerializer,
    UnitProgressUpdateSerializer,
    ContentLessonProgressUpdateSerializer
)


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer toutes les progressions de l'utilisateur connecté.
    Fournit différentes actions pour récupérer et mettre à jour les progrès.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Le queryset de base sera défini dans les sous-classes
        pass
    
    def get_serializer_class(self):
        # Le serializer sera défini dans les sous-classes
        pass
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserLessonProgressViewSet(UserProgressViewSet):
    """Gestion de la progression des leçons pour l'utilisateur connecté"""
    
    def get_queryset(self):
        return UserLessonProgress.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'update_progress':
            return LessonProgressUpdateSerializer
        return UserLessonProgressSerializer
    
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        """Mettre à jour la progression d'une leçon spécifique"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        lesson_id = serializer.validated_data['lesson_id']
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        
        # Récupérer ou créer l'objet de progression
        progress, created = UserLessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        # Si nécessaire, marquer comme commencé
        if progress.status == 'not_started':
            progress.mark_started()
        
        # Mettre à jour les champs si présents
        if 'completion_percentage' in serializer.validated_data:
            completion_percentage = serializer.validated_data['completion_percentage']
            score = serializer.validated_data.get('score')
            time_spent = serializer.validated_data.get('time_spent')
            progress.update_progress(completion_percentage, score, time_spent)
        
        # Marquer comme terminé si demandé
        if serializer.validated_data.get('mark_completed'):
            progress.mark_completed(
                score=serializer.validated_data.get('score', progress.score)
            )
        
        # Mise à jour de la progression de l'unité associée
        unit_progress, _ = UserUnitProgress.objects.get_or_create(
            user=request.user,
            unit=lesson.unit
        )
        unit_progress.update_progress()
        
        return Response(
            UserLessonProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_unit(self, request):
        """Récupérer la progression des leçons par unité"""
        unit_id = request.query_params.get('unit_id')
        if not unit_id:
            return Response(
                {"error": "Le paramètre unit_id est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        unit = get_object_or_404(Unit, pk=unit_id)
        queryset = self.get_queryset().filter(lesson__unit=unit)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserUnitProgressViewSet(UserProgressViewSet):
    """Gestion de la progression des unités pour l'utilisateur connecté"""
    
    def get_queryset(self):
        return UserUnitProgress.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'update_progress':
            return UnitProgressUpdateSerializer
        return UserUnitProgressSerializer
    
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        """Mettre à jour manuellement la progression d'une unité"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        unit_id = serializer.validated_data['unit_id']
        unit = get_object_or_404(Unit, pk=unit_id)
        
        # Récupérer ou créer l'objet de progression
        progress, created = UserUnitProgress.objects.get_or_create(
            user=request.user,
            unit=unit
        )
        
        # Recalculer la progression basée sur les leçons
        progress.update_progress()
        
        # Marquer comme terminé si demandé
        if serializer.validated_data.get('mark_completed'):
            progress.mark_completed()
        
        return Response(
            UserUnitProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """Récupérer la progression des unités par niveau"""
        level = request.query_params.get('level')
        if not level:
            return Response(
                {"error": "Le paramètre level est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        queryset = self.get_queryset().filter(unit__level=level)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContentLessonProgressViewSet(UserProgressViewSet):
    """Gestion de la progression des contenus de leçon pour l'utilisateur connecté"""
    
    def get_queryset(self):
        # Utilise UserCourseProgress avec un filtre sur le content_type
        content_type = ContentType.objects.get_for_model(ContentLesson)
        return UserCourseProgress.objects.filter(
            user=self.request.user,
            content_type=content_type
        )
    
    def get_serializer_class(self):
        if self.action == 'update_progress':
            return ContentLessonProgressUpdateSerializer
        return ContentLessonProgressSerializer
    
    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        """Mettre à jour la progression d'un contenu de leçon spécifique"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        content_lesson_id = serializer.validated_data['content_lesson_id']
        content_lesson = get_object_or_404(ContentLesson, pk=content_lesson_id)
        content_type = ContentType.objects.get_for_model(ContentLesson)
        
        # Récupérer ou créer l'objet de progression
        progress, created = UserCourseProgress.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=content_lesson_id
        )
        
        # Si nécessaire, marquer comme commencé
        if progress.status == 'not_started':
            if not progress.started_at:
                progress.mark_started()
        
        # Mettre à jour les champs si présents
        if 'completion_percentage' in serializer.validated_data:
            completion_percentage = serializer.validated_data['completion_percentage']
            score = serializer.validated_data.get('score')
            time_spent = serializer.validated_data.get('time_spent')
            xp_earned = serializer.validated_data.get('xp_earned')
            
            progress.update_progress(completion_percentage, score, time_spent)
            
            if xp_earned and xp_earned > progress.xp_earned:
                progress.xp_earned = xp_earned
                progress.save()
        
        # Marquer comme terminé si demandé
        if serializer.validated_data.get('mark_completed'):
            progress.mark_completed(
                score=serializer.validated_data.get('score', progress.score)
            )
            
            # Si XP fourni, mettre à jour
            if 'xp_earned' in serializer.validated_data:
                progress.xp_earned = serializer.validated_data['xp_earned']
                progress.save()
        
        # Mise à jour de la progression de la leçon associée
        lesson_progress, _ = UserLessonProgress.objects.get_or_create(
            user=request.user,
            lesson=content_lesson.lesson
        )
        
        # Calculer la progression de la leçon basée sur la progression des contenus
        lesson_content_items = ContentLesson.objects.filter(lesson=content_lesson.lesson)
        content_type = ContentType.objects.get_for_model(ContentLesson)
        
        content_progresses = UserCourseProgress.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id__in=lesson_content_items.values_list('id', flat=True)
        )
        
        if content_progresses.exists():
            total_items = lesson_content_items.count()
            completed_items = content_progresses.filter(status='completed').count()
            
            if completed_items == total_items:
                lesson_progress.mark_completed()
            else:
                # Calculer le pourcentage de progression
                total_percentage = sum(cp.completion_percentage for cp in content_progresses)
                avg_percentage = total_percentage // total_items if total_items > 0 else 0
                
                lesson_progress.update_progress(
                    completion_percentage=avg_percentage,
                    time_spent=sum(cp.time_spent for cp in content_progresses)
                )
        
        # Mise à jour de la progression de l'unité
        unit_progress, _ = UserUnitProgress.objects.get_or_create(
            user=request.user,
            unit=content_lesson.lesson.unit
        )
        unit_progress.update_progress()
        
        return Response(
            ContentLessonProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def by_lesson(self, request):
        """Récupérer la progression des contenus par leçon"""
        lesson_id = request.query_params.get('lesson_id')
        if not lesson_id:
            return Response(
                {"error": "Le paramètre lesson_id est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        content_lessons = ContentLesson.objects.filter(lesson_id=lesson_id)
        content_type = ContentType.objects.get_for_model(ContentLesson)
        
        queryset = self.get_queryset().filter(
            object_id__in=content_lessons.values_list('id', flat=True)
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserProgressSummaryView(generics.RetrieveAPIView):
    """Vue pour obtenir un résumé global de la progression de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        
        # Statistiques globales
        units_progress = UserUnitProgress.objects.filter(user=user)
        lessons_progress = UserLessonProgress.objects.filter(user=user)
        
        # Progression par niveau
        level_stats = {}
        for level in Unit.LEVEL_CHOICES:
            level_code = level[0]
            units_in_level = units_progress.filter(unit__level=level_code)
            
            level_stats[level_code] = {
                'total_units': units_in_level.count(),
                'completed_units': units_in_level.filter(status='completed').count(),
                'in_progress_units': units_in_level.filter(status='in_progress').count(),
                'avg_completion': 0
            }
            
            if units_in_level.exists():
                total_completion = sum(u.completion_percentage for u in units_in_level)
                level_stats[level_code]['avg_completion'] = total_completion // units_in_level.count()
        
        # Contenus récemment consultés
        recent_items = UserCourseProgress.objects.filter(user=user).order_by('-last_accessed')[:5]
        recent_items_data = UserCourseContentProgressSerializer(recent_items, many=True).data
        
        # Statistiques d'activité
        total_time_spent = sum(l.time_spent for l in lessons_progress) / 60  # En minutes
        
        return Response({
            'summary': {
                'total_units': units_progress.count(),
                'completed_units': units_progress.filter(status='completed').count(),
                'total_lessons': lessons_progress.count(),
                'completed_lessons': lessons_progress.filter(status='completed').count(),
                'total_time_spent_minutes': total_time_spent,
                'xp_earned': UserCourseProgress.objects.filter(user=user).aggregate(
                    total_xp=Sum('xp_earned')
                )['total_xp'] or 0
            },
            'level_progression': level_stats,
            'recent_activity': recent_items_data
        })