"""
API Views utilisant Django REST Framework pour l'application Language Learning
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
import json

from ..models import *
from ..serializers import (
    LanguageSerializer, UserLearningProfileSerializer, CourseUnitSerializer,
    CourseModuleSerializer, ModuleProgressSerializer, UserCourseProgressSerializer,
    UserLanguageSerializer, LearningInterfaceSerializer, ModuleStartSerializer,
    ModuleCompleteSerializer, ProgressRefreshSerializer
)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les langues disponibles"""
    queryset = Language.objects.filter(is_active=True)
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]


class UserLearningProfileViewSet(viewsets.ModelViewSet):
    """ViewSet pour le profil d'apprentissage utilisateur"""
    serializer_class = UserLearningProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLearningProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CourseUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les unités de cours"""
    serializer_class = CourseUnitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        language_code = self.request.query_params.get('language', 'EN')
        return CourseUnit.objects.filter(
            language__code=language_code,
            is_active=True
        ).order_by('order', 'unit_number')

    @action(detail=True, methods=['get'])
    def modules(self, request, pk=None):
        """Récupère les modules d'une unité avec la progression utilisateur"""
        unit = self.get_object()

        modules = CourseModule.objects.filter(
            unit=unit
        ).order_by('order', 'module_number')

        modules_data = []
        for module in modules:
            progress = ModuleProgress.objects.filter(
                user=request.user,
                module=module
            ).first()

            module_data = CourseModuleSerializer(module).data
            module_data.update({
                'is_completed': progress.is_completed if progress else False,
                'is_unlocked': module.is_available_for_user(request.user),
                'score': progress.score if progress else None,
                'attempts': progress.attempts if progress else 0,
            })
            modules_data.append(module_data)

        # Calculer la durée totale estimée
        total_duration = sum(module.estimated_duration for module in modules)

        return Response({
            'unit': {
                'id': unit.id,
                'title': unit.title,
                'description': unit.description,
                'unit_number': unit.unit_number,
                'estimated_duration': total_duration,
            },
            'modules': modules_data
        })

    @action(detail=False, methods=['get'])
    def with_progress(self, request):
        """Récupère les unités avec la progression utilisateur"""
        language_code = request.query_params.get('language', 'EN')
        language = get_object_or_404(Language, code=language_code)

        units = self.get_queryset().filter(language=language)

        units_with_progress = []
        for unit in units:
            modules_count = unit.modules.count()
            completed_modules = ModuleProgress.objects.filter(
                user=request.user,
                module__unit=unit,
                is_completed=True
            ).count()

            progress_percentage = 0
            if modules_count > 0:
                progress_percentage = int((completed_modules / modules_count) * 100)

            units_with_progress.append({
                'id': unit.id,
                'unit_number': unit.unit_number,
                'title': unit.title,
                'description': unit.description,
                'modules_count': modules_count,
                'completed_modules': completed_modules,
                'progress_percentage': progress_percentage,
            })

        return Response({
            'language': LanguageSerializer(language).data,
            'units': units_with_progress
        })


class ModuleProgressViewSet(viewsets.ModelViewSet):
    """ViewSet pour la progression des modules"""
    serializer_class = ModuleProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ModuleProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def start_module(self, request):
        """Démarre un module"""
        module_id = request.data.get('module_id')
        module = get_object_or_404(CourseModule, id=module_id)

        # Vérifier si le module est disponible
        if not module.is_available_for_user(request.user):
            return Response(
                {'error': 'Ce module est verrouillé. Complétez les modules précédents pour y accéder.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Obtenir ou créer la progression
        progress, created = ModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )

        # Incrémenter le nombre de tentatives
        progress.attempts += 1
        progress.save()

        return Response({
            'success': True,
            'module': CourseModuleSerializer(module).data,
            'progress': ModuleProgressSerializer(progress).data
        })

    @action(detail=False, methods=['post'])
    def complete_module(self, request):
        """Marque un module comme complété"""
        module_id = request.data.get('module_id')
        score = int(request.data.get('score', 100))

        module = get_object_or_404(CourseModule, id=module_id)

        progress, created = ModuleProgress.objects.get_or_create(
            user=request.user,
            module=module
        )

        progress.complete(score=score)

        # Mettre à jour les XP de l'utilisateur
        user_progress = UserCourseProgress.objects.filter(
            user=request.user,
            language=module.unit.language
        ).first()

        if user_progress:
            user_progress.total_xp += module.xp_reward
            # Calculer le niveau (100 XP par niveau)
            user_progress.level = (user_progress.total_xp // 100) + 1
            user_progress.save()

        return Response({
            'success': True,
            'xp_earned': module.xp_reward,
            'total_xp': user_progress.total_xp if user_progress else 0,
            'level': user_progress.level if user_progress else 1,
        })


class UserCourseProgressViewSet(viewsets.ModelViewSet):
    """ViewSet pour la progression utilisateur dans les cours"""
    serializer_class = UserCourseProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCourseProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def refresh(self, request):
        """Rafraîchit les données de progression"""
        selected_language = request.query_params.get('lang', 'EN')

        context_data = {
            'selected_language': selected_language,
            'user_progress': {
                'level': 1,
                'total_xp': 0,
                'get_completion_percentage': 0,
            },
            'user_streak': 0,
        }

        try:
            # Récupérer le profil d'apprentissage de l'utilisateur
            learning_profile = request.user.learning_profile
            context_data['user_progress'].update({
                'level': getattr(learning_profile, 'language_level', 'A1'),
                'total_xp': getattr(learning_profile, 'total_time_spent', 0) * 10,  # Convertir minutes en XP
                'get_completion_percentage': getattr(learning_profile, 'progress_percentage', 0),
            })
            context_data['user_streak'] = getattr(learning_profile, 'streak_count', 0)
        except AttributeError:
            # Pas encore de profil d'apprentissage - utiliser les valeurs par défaut
            pass

        return Response(context_data)


class LearningInterfaceViewSet(viewsets.ViewSet):
    """ViewSet pour l'interface d'apprentissage principale"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Interface principale d'apprentissage"""
        selected_language = request.query_params.get('lang', '')
        view_type = request.query_params.get('view', 'home')

        # Si aucune langue n'est sélectionnée, utiliser la langue cible de l'utilisateur
        if not selected_language:
            try:
                learning_profile = request.user.learning_profile
                selected_language = learning_profile.target_language
            except AttributeError:
                # Si pas de profil d'apprentissage, créer un profil par défaut
                learning_profile = UserLearningProfile.objects.create(user=request.user)
                selected_language = learning_profile.target_language

        # En dernier recours, utiliser une langue par défaut
        if not selected_language:
            selected_language = 'EN'

        context = {
            'selected_language': selected_language,
            'selected_language_name': '',
            'course_units': [],
            'active_unit': None,
            'active_unit_modules': [],
            'user_progress': None,
            'user_streak': 0,
            'view_type': view_type,
        }

        # Obtenir la langue sélectionnée
        language = Language.objects.filter(code=selected_language).first()
        if language:
            context['selected_language_name'] = language.name

            # Obtenir ou créer la progression de l'utilisateur
            user_progress, created = UserCourseProgress.objects.get_or_create(
                user=request.user,
                language=language
            )
            context['user_progress'] = UserCourseProgressSerializer(user_progress).data

            # Obtenir les unités avec progression
            units = CourseUnit.objects.filter(
                language=language,
                is_active=True
            ).order_by('order', 'unit_number')

            units_with_progress = []
            for unit in units:
                modules_count = unit.modules.count()
                completed_modules = ModuleProgress.objects.filter(
                    user=request.user,
                    module__unit=unit,
                    is_completed=True
                ).count()

                progress_percentage = 0
                if modules_count > 0:
                    progress_percentage = int((completed_modules / modules_count) * 100)

                units_with_progress.append({
                    'id': unit.id,
                    'unit_number': unit.unit_number,
                    'title': unit.title,
                    'description': unit.description,
                    'modules_count': modules_count,
                    'completed_modules': completed_modules,
                    'progress_percentage': progress_percentage,
                })

            context['course_units'] = units_with_progress

            # Calculer le streak
            user_language = UserLanguage.objects.filter(
                user=request.user,
                language=language
            ).first()
            if user_language:
                context['user_streak'] = user_language.streak_count

        return Response(context)

    @action(detail=False, methods=['get'])
    def navbar(self, request):
        """Données pour la navbar"""
        selected_language = request.query_params.get('lang', 'EN')

        language = Language.objects.filter(code=selected_language).first()
        user_streak = 0

        if language:
            user_language = UserLanguage.objects.filter(
                user=request.user,
                language=language
            ).first()
            if user_language:
                user_streak = user_language.streak_count

        return Response({
            'selected_language': selected_language,
            'selected_language_name': language.name if language else '',
            'user_streak': user_streak,
        })

    @action(detail=False, methods=['get'])
    def progress_panel(self, request):
        """Données pour le panneau de progression"""
        selected_language = request.query_params.get('lang', 'EN')

        language = Language.objects.filter(code=selected_language).first()
        user_streak = 0
        units_count = 0

        if language:
            units_count = CourseUnit.objects.filter(
                language=language,
                is_active=True
            ).count()

            user_language = UserLanguage.objects.filter(
                user=request.user,
                language=language
            ).first()
            if user_language:
                user_streak = user_language.streak_count

        return Response({
            'user_streak': user_streak,
            'course_units_count': units_count,
        })


class UserLanguageViewSet(viewsets.ModelViewSet):
    """ViewSet pour les langues de l'utilisateur"""
    serializer_class = UserLanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLanguage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)