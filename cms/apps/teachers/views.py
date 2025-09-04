from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, UpdateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum
from datetime import datetime, timedelta
from .models import Teacher, TeacherLanguage, TeacherQualification, TeacherAvailability, TeacherAnnouncement
from apps.scheduling.models import PrivateLesson

class TeacherDashboardView(LoginRequiredMixin, DetailView):
    """Main teacher dashboard with overview."""
    model = Teacher
    template_name = 'teachers/dashboard.html'
    context_object_name = 'teacher'
    
    def get_object(self):
        teacher, created = Teacher.objects.get_or_create(
            user=self.request.user,
            defaults={
                'status': Teacher.Status.PENDING,
                'hourly_rate': 25.00
            }
        )
        return teacher
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.get_object()
        
        # Upcoming lessons
        upcoming_lessons = PrivateLesson.objects.filter(
            teacher=teacher,
            scheduled_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('scheduled_date')[:5]
        
        # Recent lessons for quick access
        recent_lessons = PrivateLesson.objects.filter(
            teacher=teacher
        ).order_by('-scheduled_date')[:10]
        
        # Statistics
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        stats = {
            'total_lessons': PrivateLesson.objects.filter(teacher=teacher).count(),
            'completed_lessons': PrivateLesson.objects.filter(
                teacher=teacher, status='completed'
            ).count(),
            'this_week_lessons': PrivateLesson.objects.filter(
                teacher=teacher,
                scheduled_date__date__gte=week_start,
                status='completed'
            ).count(),
            'this_month_earnings': PrivateLesson.objects.filter(
                teacher=teacher,
                scheduled_date__date__gte=month_start,
                status='completed'
            ).aggregate(total=Sum('total_price'))['total'] or 0,
            'pending_lessons': upcoming_lessons.filter(status='scheduled').count(),
        }
        
        context.update({
            'upcoming_lessons': upcoming_lessons,
            'recent_lessons': recent_lessons,
            'stats': stats,
            'has_setup_profile': self.teacher_profile_complete(teacher),
        })
        return context
    
    def teacher_profile_complete(self, teacher):
        """Check if teacher profile is complete."""
        return all([
            teacher.bio_fr or teacher.bio_en,
            teacher.hourly_rate,
            teacher.languages.exists(),
            teacher.availability.exists()
        ])

class TeacherProfileView(LoginRequiredMixin, DetailView):
    """Teacher profile view."""
    model = Teacher
    template_name = 'teachers/profile.html'
    context_object_name = 'teacher'
    
    def get_object(self):
        return get_object_or_404(Teacher, user=self.request.user)

class TeacherProfileEditView(LoginRequiredMixin, UpdateView):
    """Teacher profile edit view."""
    model = Teacher
    template_name = 'teachers/profile_edit.html'
    fields = ['bio_en', 'bio_fr', 'bio_es', 'bio_nl', 'profile_picture', 
              'phone_number', 'country', 'city', 'hourly_rate', 'timezone',
              'max_students_per_class', 'available_for_individual', 'available_for_group']
    success_url = reverse_lazy('teachers:dashboard')
    
    def get_object(self):
        return get_object_or_404(Teacher, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Profil mis à jour avec succès !')
        return super().form_valid(form)

class TeacherLessonsView(LoginRequiredMixin, ListView):
    """View to manage teacher's lessons."""
    model = PrivateLesson
    template_name = 'teachers/lessons.html'
    context_object_name = 'lessons'
    paginate_by = 20
    
    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        queryset = PrivateLesson.objects.filter(teacher=teacher)
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(scheduled_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(scheduled_date__date__lte=date_to)
        
        return queryset.order_by('-scheduled_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = get_object_or_404(Teacher, user=self.request.user)
        
        context.update({
            'teacher': teacher,
            'status_choices': PrivateLesson.Status.choices,
            'current_status': self.request.GET.get('status', ''),
            'current_date_from': self.request.GET.get('date_from', ''),
            'current_date_to': self.request.GET.get('date_to', ''),
        })
        return context

class TeacherAvailabilityView(LoginRequiredMixin, ListView):
    """Manage teacher availability schedule."""
    model = TeacherAvailability
    template_name = 'teachers/availability.html'
    context_object_name = 'availability_slots'
    
    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return TeacherAvailability.objects.filter(teacher=teacher).order_by('day_of_week', 'start_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = get_object_or_404(Teacher, user=self.request.user)
        
        context.update({
            'teacher': teacher,
            'day_choices': TeacherAvailability.DayOfWeek.choices,
        })
        return context

class AddAvailabilitySlotView(LoginRequiredMixin, CreateView):
    """Add new availability slot."""
    model = TeacherAvailability
    template_name = 'teachers/add_availability.html'
    fields = ['day_of_week', 'start_time', 'end_time']
    success_url = reverse_lazy('teachers:availability')
    
    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        form.instance.teacher = teacher
        messages.success(self.request, 'Créneau de disponibilité ajouté !')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = get_object_or_404(Teacher, user=self.request.user)
        return context

class TeacherAnnouncementsView(LoginRequiredMixin, ListView):
    """Manage teacher announcements and offers."""
    model = TeacherAnnouncement
    template_name = 'teachers/announcements.html'
    context_object_name = 'announcements'
    paginate_by = 10
    
    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return TeacherAnnouncement.objects.filter(teacher=teacher).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = get_object_or_404(Teacher, user=self.request.user)
        
        # Statistics
        stats = {
            'total_announcements': TeacherAnnouncement.objects.filter(teacher=teacher).count(),
            'active_announcements': TeacherAnnouncement.objects.filter(
                teacher=teacher, status='active'
            ).count(),
            'total_views': TeacherAnnouncement.objects.filter(teacher=teacher).aggregate(
                total=Sum('view_count'))['total'] or 0,
            'total_bookings': TeacherAnnouncement.objects.filter(teacher=teacher).aggregate(
                total=Sum('booking_count'))['total'] or 0,
        }
        
        context.update({
            'teacher': teacher,
            'stats': stats,
            'announcement_types': TeacherAnnouncement.AnnouncementType.choices,
            'announcement_statuses': TeacherAnnouncement.Status.choices,
        })
        return context

class CreateAnnouncementView(LoginRequiredMixin, CreateView):
    """Create new teacher announcement."""
    model = TeacherAnnouncement
    template_name = 'teachers/announcement_form.html'
    fields = ['type', 'title', 'description', 'title_fr', 'description_fr', 
              'discount_percentage', 'special_price', 'start_date', 'end_date',
              'languages', 'levels', 'is_featured', 'show_on_profile', 'send_notification']
    success_url = reverse_lazy('teachers:announcements')
    
    def form_valid(self, form):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        form.instance.teacher = teacher
        messages.success(self.request, 'Annonce créée avec succès !')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = get_object_or_404(Teacher, user=self.request.user)
        context['form_title'] = 'Créer une nouvelle annonce'
        return context

class EditAnnouncementView(LoginRequiredMixin, UpdateView):
    """Edit teacher announcement."""
    model = TeacherAnnouncement
    template_name = 'teachers/announcement_form.html'
    fields = ['type', 'title', 'description', 'title_fr', 'description_fr', 
              'discount_percentage', 'special_price', 'start_date', 'end_date',
              'languages', 'levels', 'is_featured', 'show_on_profile', 'send_notification']
    success_url = reverse_lazy('teachers:announcements')
    
    def get_queryset(self):
        teacher = get_object_or_404(Teacher, user=self.request.user)
        return TeacherAnnouncement.objects.filter(teacher=teacher)
    
    def form_valid(self, form):
        messages.success(self.request, 'Annonce mise à jour avec succès !')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teacher'] = get_object_or_404(Teacher, user=self.request.user)
        context['form_title'] = 'Modifier l\'annonce'
        return context