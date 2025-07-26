"""
Teaching services for business logic.
"""
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta, time
from typing import List, Dict, Any
from .models import Teacher, PrivateLesson, TeacherAvailability, TeacherScheduleOverride
# Import updated to use course app models after learning app fusion  
from apps.course.models import StudentCourse

class BookingService:
    """Service for lesson booking logic."""
    
    def is_time_slot_available(self, teacher: Teacher, scheduled_datetime: datetime, duration_minutes: int) -> bool:
        """Check if a time slot is available for booking."""
        
        # Check if teacher is generally available
        if not teacher.is_available_for_booking:
            return False
        
        # Check for existing bookings at this time
        end_time = scheduled_datetime + timedelta(minutes=duration_minutes)
        
        existing_lessons = PrivateLesson.objects.filter(
            teacher=teacher,
            status__in=['pending', 'confirmed', 'in_progress'],
            scheduled_datetime__lt=end_time,
            scheduled_datetime__gte=scheduled_datetime - timedelta(minutes=180)  # Check 3 hours window
        )
        
        # Check for overlaps
        for lesson in existing_lessons:
            lesson_end = lesson.scheduled_datetime + timedelta(minutes=lesson.duration_minutes)
            if (scheduled_datetime < lesson_end and end_time > lesson.scheduled_datetime):
                return False
        
        # Check weekly availability
        day_of_week = scheduled_datetime.weekday() + 1  # Django uses 1-7
        lesson_time = scheduled_datetime.time()
        
        weekly_availability = TeacherAvailability.objects.filter(
            teacher=teacher,
            day_of_week=day_of_week,
            is_active=True,
            start_time__lte=lesson_time,
            end_time__gte=lesson_time
        ).exists()
        
        # Check for schedule overrides
        schedule_override = TeacherScheduleOverride.objects.filter(
            teacher=teacher,
            date=scheduled_datetime.date()
        ).first()
        
        if schedule_override:
            if not schedule_override.is_available:
                return False
            if (schedule_override.start_time and schedule_override.end_time and
                not (schedule_override.start_time <= lesson_time <= schedule_override.end_time)):
                return False
        elif not weekly_availability:
            return False
        
        return True
    
    def get_teacher_availability(self, teacher: Teacher, start_date, end_date) -> List[Dict]:
        """Get detailed availability for a teacher in a date range."""
        availability = []
        current_date = start_date
        
        while current_date <= end_date:
            day_slots = self._get_day_availability(teacher, current_date)
            if day_slots:
                availability.append({
                    'date': current_date.isoformat(),
                    'slots': day_slots
                })
            current_date += timedelta(days=1)
        
        return availability
    
    def _get_day_availability(self, teacher: Teacher, date) -> List[Dict]:
        """Get available time slots for a specific day."""
        day_of_week = date.weekday() + 1
        
        # Check for schedule override
        override = TeacherScheduleOverride.objects.filter(
            teacher=teacher,
            date=date
        ).first()
        
        if override and not override.is_available:
            return []
        
        # Get base availability
        if override and override.start_time and override.end_time:
            slots = [(override.start_time, override.end_time)]
        else:
            weekly_availability = TeacherAvailability.objects.filter(
                teacher=teacher,
                day_of_week=day_of_week,
                is_active=True
            ).order_by('start_time')
            
            slots = [(av.start_time, av.end_time) for av in weekly_availability]
        
        # Remove booked slots
        available_slots = []
        for start_time, end_time in slots:
            slot_times = self._generate_time_slots(start_time, end_time, 60)  # 60-minute slots
            
            for slot_start, slot_end in slot_times:
                slot_datetime = timezone.make_aware(
                    datetime.combine(date, slot_start)
                )
                
                if self.is_time_slot_available(teacher, slot_datetime, 60):
                    available_slots.append({
                        'start_time': slot_start.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M'),
                        'datetime': slot_datetime.isoformat()
                    })
        
        return available_slots
    
    def _generate_time_slots(self, start_time: time, end_time: time, duration_minutes: int) -> List[tuple]:
        """Generate time slots of specified duration."""
        slots = []
        current = datetime.combine(timezone.now().date(), start_time)
        end = datetime.combine(timezone.now().date(), end_time)
        
        while current + timedelta(minutes=duration_minutes) <= end:
            slot_end = current + timedelta(minutes=duration_minutes)
            slots.append((current.time(), slot_end.time()))
            current = slot_end
        
        return slots

class TeacherMatchingService:
    """Service for matching students with suitable teachers."""
    
    def __init__(self, student):
        self.student = student
    
    def get_recommendations(self, limit: int = 5) -> List[Teacher]:
        """Get personalized teacher recommendations."""
        
        # Get student's learning history
        student_courses = StudentCourse.objects.filter(student=self.student)
        
        # Extract preferences
        preferred_languages = self._get_preferred_languages(student_courses)
        student_level = self._estimate_student_level(student_courses)
        
        # Get available teachers
        available_teachers = Teacher.objects.filter(
            status='active',
            available_for_individual=True
        ).annotate(
            rating_count=Count('teaching_sessions__rating'),
            avg_rating=Avg('teaching_sessions__rating__overall_rating')
        )
        
        # Score and rank teachers
        scored_teachers = []
        for teacher in available_teachers:
            score = self._calculate_teacher_score(teacher, preferred_languages, student_level)
            scored_teachers.append((teacher, score))
        
        # Sort by score and return top recommendations
        scored_teachers.sort(key=lambda x: x[1], reverse=True)
        return [teacher for teacher, score in scored_teachers[:limit]]
    
    def _get_preferred_languages(self, student_courses) -> List[str]:
        """Extract preferred languages from student's course history."""
        # This would need to be adapted based on your course model structure
        # For now, return common languages
        return ['en', 'fr', 'es']
    
    def _estimate_student_level(self, student_courses) -> str:
        """Estimate student's current level."""
        if not student_courses.exists():
            return 'A1'
        
        # Get the highest level from completed courses
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        completed_levels = []
        
        for course in student_courses.filter(progress_percentage__gte=80):
            if hasattr(course.unit, 'level') and course.unit.level in levels:
                completed_levels.append(course.unit.level)
        
        if not completed_levels:
            return 'A1'
        
        # Return the highest completed level
        highest_level_index = max(levels.index(level) for level in completed_levels)
        return levels[min(highest_level_index + 1, len(levels) - 1)]  # Next level or max
    
    def _calculate_teacher_score(self, teacher: Teacher, preferred_languages: List[str], student_level: str) -> float:
        """Calculate matching score for a teacher."""
        score = 0.0
        
        # Language match (40% weight)
        teacher_languages = teacher.teaching_languages.values_list('language_code', flat=True)
        language_match = len(set(preferred_languages) & set(teacher_languages)) / len(preferred_languages)
        score += language_match * 0.4
        
        # Rating (30% weight)
        if teacher.average_rating > 0:
            score += (teacher.average_rating / 5.0) * 0.3
        
        # Experience (20% weight)
        experience_score = min(teacher.years_experience / 10.0, 1.0)  # Cap at 10 years
        score += experience_score * 0.2
        
        # Availability (10% weight)
        # Check if teacher has availability in the next week
        next_week = timezone.now().date() + timedelta(days=7)
        booking_service = BookingService()
        availability = booking_service.get_teacher_availability(teacher, timezone.now().date(), next_week)
        availability_score = 1.0 if availability else 0.0
        score += availability_score * 0.1
        
        return score
    
    def get_recommendation_reasons(self) -> Dict[str, str]:
        """Get explanation for recommendation logic."""
        return {
            'language_match': 'Teachers who speak your learning languages',
            'high_rating': 'Highly rated teachers with excellent reviews',
            'experienced': 'Teachers with years of teaching experience',
            'available': 'Teachers with immediate availability',
            'student_level': 'Teachers suitable for your current level'
        }

class TeachingAnalyticsService:
    """Service for teaching analytics and reporting."""
    
    @staticmethod
    def update_teacher_analytics(teacher: Teacher, date=None):
        """Update daily analytics for a teacher."""
        if date is None:
            date = timezone.now().date()
        
        from .models import TeachingAnalytics
        
        # Get or create analytics record
        analytics, created = TeachingAnalytics.objects.get_or_create(
            teacher=teacher,
            date=date,
            defaults={
                'lessons_scheduled': 0,
                'lessons_completed': 0,
                'lessons_cancelled': 0,
                'no_shows': 0,
                'total_teaching_minutes': 0,
                'gross_earnings': 0,
                'net_earnings': 0
            }
        )
        
        # Calculate metrics for the day
        day_lessons = PrivateLesson.objects.filter(
            teacher=teacher,
            scheduled_datetime__date=date
        )
        
        analytics.lessons_scheduled = day_lessons.count()
        analytics.lessons_completed = day_lessons.filter(status='completed').count()
        analytics.lessons_cancelled = day_lessons.filter(
            status__in=['cancelled_student', 'cancelled_teacher']
        ).count()
        analytics.no_shows = day_lessons.filter(
            status__in=['no_show_student', 'no_show_teacher']
        ).count()
        
        # Calculate earnings
        completed_lessons = day_lessons.filter(status='completed')
        analytics.gross_earnings = sum(lesson.total_price for lesson in completed_lessons)
        analytics.net_earnings = analytics.gross_earnings * 0.85  # 15% platform fee
        
        # Calculate total teaching time
        total_minutes = sum(lesson.duration_minutes for lesson in completed_lessons)
        analytics.total_teaching_minutes = total_minutes
        
        # Calculate average rating for the day
        day_ratings = []
        for lesson in completed_lessons:
            if hasattr(lesson, 'rating'):
                day_ratings.append(lesson.rating.overall_rating)
        
        analytics.average_session_rating = (
            sum(day_ratings) / len(day_ratings) if day_ratings else 0
        )
        
        analytics.save()
        return analytics