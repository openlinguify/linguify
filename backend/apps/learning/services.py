"""
Learning services for business logic and recommendations.
"""
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from typing import List, Dict, Any
from .models import (StudentCourse, StudentLessonProgress, LearningAnalytics,
                     StudentReview, LearningSession)
from apps.course.models.core import Unit

class LearningService:
    """Service for learning-related business logic."""
    
    def __init__(self, student):
        self.student = student
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary for student."""
        
        # Course statistics
        enrolled_courses = StudentCourse.objects.filter(student=self.student)
        active_courses = enrolled_courses.filter(status='active')
        completed_courses = enrolled_courses.filter(progress_percentage=100)
        
        # Time statistics
        total_time = enrolled_courses.aggregate(
            total=Sum('time_spent_minutes')
        )['total'] or 0
        
        # Streak calculation
        current_streak = self._calculate_current_streak()
        
        # Recent activity
        recent_sessions = LearningSession.objects.filter(
            student=self.student
        ).select_related(
            'student_course__unit', 'lesson'
        ).order_by('-started_at')[:5]
        
        # Progress summary
        progress_summary = self._get_progress_summary()
        
        # Recommended courses
        recommendation_service = RecommendationService(self.student)
        recommended_courses = recommendation_service.get_recommendations(limit=3)
        
        return {
            'active_courses': active_courses.count(),
            'completed_courses': completed_courses.count(),
            'total_time_spent': total_time,
            'current_streak': current_streak,
            'recent_activity': recent_sessions,
            'progress_summary': progress_summary,
            'recommended_courses': recommended_courses
        }
    
    def _calculate_current_streak(self) -> int:
        """Calculate current learning streak in days."""
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        while True:
            # Check if student had learning activity on current_date
            has_activity = LearningSession.objects.filter(
                student=self.student,
                started_at__date=current_date
            ).exists()
            
            if has_activity:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def _get_progress_summary(self) -> Dict[str, Any]:
        """Get detailed progress summary."""
        enrolled_courses = StudentCourse.objects.filter(
            student=self.student,
            status='active'
        )
        
        progress_data = {
            'courses_by_progress': {
                'not_started': 0,
                'in_progress': 0,
                'completed': 0
            },
            'average_progress': 0,
            'total_lessons': 0,
            'completed_lessons': 0
        }
        
        for course in enrolled_courses:
            if course.progress_percentage == 0:
                progress_data['courses_by_progress']['not_started'] += 1
            elif course.progress_percentage == 100:
                progress_data['courses_by_progress']['completed'] += 1
            else:
                progress_data['courses_by_progress']['in_progress'] += 1
        
        # Calculate averages
        if enrolled_courses.exists():
            avg_progress = enrolled_courses.aggregate(
                avg=Avg('progress_percentage')
            )['avg']
            progress_data['average_progress'] = round(avg_progress, 1) if avg_progress else 0
        
        # Lesson statistics
        total_lessons = StudentLessonProgress.objects.filter(
            student_course__student=self.student
        ).count()
        
        completed_lessons = StudentLessonProgress.objects.filter(
            student_course__student=self.student,
            status='completed'
        ).count()
        
        progress_data['total_lessons'] = total_lessons
        progress_data['completed_lessons'] = completed_lessons
        
        return progress_data
    
    def update_daily_analytics(self, date=None):
        """Update daily learning analytics for student."""
        if date is None:
            date = timezone.now().date()
        
        # Get or create analytics record
        analytics, created = LearningAnalytics.objects.get_or_create(
            student=self.student,
            date=date,
            defaults={
                'total_time_minutes': 0,
                'lessons_started': 0,
                'lessons_completed': 0,
                'exercises_completed': 0,
                'sessions_count': 0,
                'unique_courses_accessed': 0
            }
        )
        
        # Calculate metrics for the day
        sessions = LearningSession.objects.filter(
            student=self.student,
            started_at__date=date
        )
        
        analytics.sessions_count = sessions.count()
        analytics.total_time_minutes = sum(
            session.duration_seconds // 60 for session in sessions
        )
        analytics.exercises_completed = sum(
            session.exercises_completed for session in sessions
        )
        analytics.unique_courses_accessed = sessions.values(
            'student_course'
        ).distinct().count()
        
        # Lessons started and completed on this day
        analytics.lessons_started = StudentLessonProgress.objects.filter(
            student_course__student=self.student,
            started_at__date=date
        ).count()
        
        analytics.lessons_completed = StudentLessonProgress.objects.filter(
            student_course__student=self.student,
            completed_at__date=date
        ).count()
        
        # Calculate average score from completed content
        content_scores = []
        for session in sessions:
            if session.lesson:
                lesson_content = session.lesson.content_lessons.all()
                for content in lesson_content:
                    try:
                        progress = content.student_content_progress.get(
                            lesson_progress__student_course__student=self.student
                        )
                        if progress.completed_at and progress.completed_at.date() == date:
                            content_scores.append(progress.score)
                    except:
                        continue
        
        analytics.average_score = sum(content_scores) // len(content_scores) if content_scores else 0
        
        # Update streak
        yesterday = date - timedelta(days=1)
        yesterday_analytics = LearningAnalytics.objects.filter(
            student=self.student,
            date=yesterday
        ).first()
        
        if analytics.total_time_minutes > 0:  # Had activity today
            if yesterday_analytics and yesterday_analytics.streak_days > 0:
                analytics.streak_days = yesterday_analytics.streak_days + 1
            else:
                analytics.streak_days = 1
        else:
            analytics.streak_days = 0
        
        analytics.save()
        return analytics

class RecommendationService:
    """Service for course recommendations."""
    
    def __init__(self, student):
        self.student = student
    
    def get_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get personalized course recommendations."""
        
        # Get student's course history
        enrolled_courses = StudentCourse.objects.filter(
            student=self.student
        ).select_related('unit')
        
        # Extract preferences
        preferred_levels = self._get_preferred_levels(enrolled_courses)
        preferred_teachers = self._get_preferred_teachers(enrolled_courses)
        
        # Get available courses (not yet purchased)
        purchased_unit_ids = enrolled_courses.values_list('unit_id', flat=True)
        available_units = Unit.objects.exclude(
            id__in=purchased_unit_ids
        ).annotate(
            avg_rating=Avg('student_enrollments__reviews__rating'),
            review_count=Count('student_enrollments__reviews'),
            enrollment_count=Count('student_enrollments')
        )
        
        recommendations = []
        
        # Level-based recommendations
        for level in preferred_levels[:2]:  # Top 2 preferred levels
            level_courses = available_units.filter(level=level).order_by(
                '-avg_rating', '-enrollment_count'
            )[:2]
            
            for course in level_courses:
                recommendations.append({
                    'unit': course,
                    'match_score': 0.8,
                    'reason': f'Based on your {level} level courses'
                })
        
        # Teacher-based recommendations
        for teacher_id in preferred_teachers[:2]:
            teacher_courses = available_units.filter(
                # Assuming teacher info is stored in Unit model
                # You might need to adjust this based on your actual model structure
            ).order_by('-avg_rating')[:1]
            
            for course in teacher_courses:
                recommendations.append({
                    'unit': course,
                    'match_score': 0.7,
                    'reason': 'From teachers you\'ve studied with before'
                })
        
        # Popular courses
        popular_courses = available_units.order_by(
            '-enrollment_count', '-avg_rating'
        )[:3]
        
        for course in popular_courses:
            if course not in [r['unit'] for r in recommendations]:
                recommendations.append({
                    'unit': course,
                    'match_score': 0.6,
                    'reason': 'Popular among other students'
                })
        
        # Sort by match score and limit
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:limit]
    
    def _get_preferred_levels(self, enrolled_courses) -> List[str]:
        """Get student's preferred course levels."""
        level_counts = {}
        for course in enrolled_courses:
            level = course.unit.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        return sorted(level_counts.keys(), key=level_counts.get, reverse=True)
    
    def _get_preferred_teachers(self, enrolled_courses) -> List[int]:
        """Get student's preferred teachers."""
        teacher_counts = {}
        for course in enrolled_courses:
            teacher_id = course.teacher_id
            teacher_counts[teacher_id] = teacher_counts.get(teacher_id, 0) + 1
        
        return sorted(teacher_counts.keys(), key=teacher_counts.get, reverse=True)
    
    def get_recommendation_reasons(self) -> Dict[str, str]:
        """Get explanation for recommendation logic."""
        return {
            'level_based': 'Courses matching your current learning level',
            'teacher_based': 'From instructors you\'ve learned with before',
            'popular': 'Highly rated courses popular with other students',
            'similar_students': 'Courses taken by students with similar interests',
            'completion_rate': 'Courses with high completion rates'
        }

class ProgressTrackingService:
    """Service for tracking and calculating learning progress."""
    
    @staticmethod
    def calculate_course_progress(student_course: StudentCourse) -> int:
        """Calculate accurate course progress percentage."""
        total_lessons = student_course.unit.lessons.count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = StudentLessonProgress.objects.filter(
            student_course=student_course,
            status='completed'
        ).count()
        
        return int((completed_lessons / total_lessons) * 100)
    
    @staticmethod
    def calculate_lesson_progress(lesson_progress: StudentLessonProgress) -> int:
        """Calculate lesson progress based on content completion."""
        total_content = lesson_progress.lesson.content_lessons.count()
        if total_content == 0:
            return 100 if lesson_progress.status == 'completed' else 0
        
        completed_content = lesson_progress.content_progress.filter(
            is_completed=True
        ).count()
        
        return int((completed_content / total_content) * 100)
    
    @staticmethod
    def update_all_progress(student_course: StudentCourse):
        """Update all progress calculations for a course."""
        # Update lesson progress
        for lesson_progress in student_course.lesson_progress.all():
            progress = ProgressTrackingService.calculate_lesson_progress(lesson_progress)
            lesson_progress.progress_percentage = progress
            lesson_progress.save(update_fields=['progress_percentage'])
        
        # Update course progress
        course_progress = ProgressTrackingService.calculate_course_progress(student_course)
        student_course.progress_percentage = course_progress
        student_course.save(update_fields=['progress_percentage'])