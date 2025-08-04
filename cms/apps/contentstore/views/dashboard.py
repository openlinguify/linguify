"""
Dashboard and course management views for contentstore.
Replaces course_builder with OpenEdX-style interface.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from apps.teachers.models import Teacher
from ..models import CMSUnit
from ..models import CourseSettings
from ..forms import CourseCreateForm
from ..services.translation import translation_service


class TeacherRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a teacher."""
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            messages.error(request, "Vous devez avoir un profil enseignant pour accéder à cette page.")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CourseListView(TeacherRequiredMixin, ListView):
    """
    Main course list view following OpenEdX patterns.
    Replaces course_builder course list.
    """
    model = CMSUnit
    template_name = 'contentstore/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        """Get courses for current teacher."""
        return CMSUnit.objects.filter(teacher=self.request.user.teacher_profile).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teacher = self.request.user.teacher_profile
        
        # Add statistics
        context.update({
            'total_courses': self.get_queryset().count(),
            'published_courses': self.get_queryset().filter(is_published=True).count(),
            'draft_courses': self.get_queryset().filter(is_published=False).count(),
            'synced_courses': self.get_queryset().filter(sync_status='synced').count(),
            'teacher': teacher,
        })
        
        return context


class CourseCreateView(TeacherRequiredMixin, CreateView):
    """
    Course creation view following OpenEdX patterns.
    """
    model = CMSUnit
    template_name = 'contentstore/course_create.html'
    form_class = CourseCreateForm
    
    def form_valid(self, form):
        """Set teacher, generate translations, and create course settings."""
        form.instance.teacher = self.request.user.teacher_profile
        form.instance.order = CMSUnit.objects.filter(teacher=self.request.user.teacher_profile).count() + 1
        
        # Generate automatic translations if French content is provided
        title_fr = form.cleaned_data.get('title_fr', '')
        description_fr = form.cleaned_data.get('description_fr', '')
        
        if title_fr or description_fr:
            try:
                # Get translations from the translation service
                translations = translation_service.translate_course_content(title_fr, description_fr)
                
                # Apply translations to the form instance
                form.instance.title_en = translations['title_en'] or title_fr
                form.instance.title_es = translations['title_es'] or title_fr
                form.instance.title_nl = translations['title_nl'] or title_fr
                form.instance.description_en = translations['description_en'] or description_fr
                form.instance.description_es = translations['description_es'] or description_fr
                form.instance.description_nl = translations['description_nl'] or description_fr
                
                messages.info(self.request, 'Traductions automatiques générées avec succès!')
                
            except Exception as e:
                # Log the error but don't fail the course creation
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Translation failed for course creation: {e}")
                
                # Use fallback (French content for all languages)
                form.instance.title_en = title_fr
                form.instance.title_es = title_fr
                form.instance.title_nl = title_fr
                form.instance.description_en = description_fr
                form.instance.description_es = description_fr
                form.instance.description_nl = description_fr
                
                messages.warning(self.request, 'Traduction automatique non disponible. Le contenu français sera utilisé pour toutes les langues.')
        
        response = super().form_valid(form)
        
        # Create course settings automatically
        CourseSettings.objects.get_or_create(
            course_id=str(self.object.id),
            defaults={
                'display_name': self.object.title,
                'short_description': self.object.description or '',
                'language': 'fr',
            }
        )
        
        messages.success(self.request, f'Cours "{self.object.title}" créé avec succès!')
        return response
    
    def get_success_url(self):
        """Redirect to studio after creation."""
        return reverse_lazy('contentstore:course_studio', kwargs={'course_id': self.object.pk})


class CourseDetailView(TeacherRequiredMixin, DetailView):
    """
    Course detail view with overview and quick actions.
    """
    model = CMSUnit
    template_name = 'contentstore/course_detail.html'
    context_object_name = 'course'
    
    def get_queryset(self):
        """Ensure teacher owns the course."""
        return CMSUnit.objects.filter(teacher=self.request.user.teacher_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get course settings
        course_settings, _ = CourseSettings.objects.get_or_create(
            course_id=str(self.object.id),
            defaults={
                'display_name': self.object.title,
                'short_description': self.object.description or '',
                'language': 'fr',
            }
        )
        
        context.update({
            'course_settings': course_settings,
            'chapters_count': self.object.chapters.count(),
            'lessons_count': self.object.lessons.count(),
            'total_duration': sum(lesson.estimated_duration for lesson in self.object.lessons.all()),
        })
        
        return context


class CourseEditView(TeacherRequiredMixin, UpdateView):
    """
    Basic course editing view for metadata.
    Advanced editing is done in Studio.
    """
    model = CMSUnit
    template_name = 'contentstore/course_edit.html'
    fields = [
        'title_en', 'title_fr', 'title_es', 'title_nl',
        'description_en', 'description_fr', 'description_es', 'description_nl',
        'level', 'price', 'is_published'
    ]
    
    def get_queryset(self):
        """Ensure teacher owns the course."""
        return CMSUnit.objects.filter(teacher=self.request.user.teacher_profile)
    
    def form_valid(self, form):
        """Update course settings when course is saved."""
        response = super().form_valid(form)
        
        # Update course settings
        course_settings, _ = CourseSettings.objects.get_or_create(
            course_id=str(self.object.id),
            defaults={
                'display_name': self.object.title,
                'short_description': self.object.description or '',
                'language': 'fr',
            }
        )
        
        course_settings.display_name = self.object.title
        course_settings.short_description = self.object.description or ''
        course_settings.save()
        
        messages.success(self.request, f'Cours "{self.object.title}" mis à jour avec succès!')
        return response
    
    def get_success_url(self):
        """Redirect back to course detail."""
        return reverse_lazy('contentstore:course_detail', kwargs={'pk': self.object.pk})


@login_required
def dashboard_view(request):
    """
    Main teacher dashboard view following OpenEdX patterns.
    """
    if not hasattr(request.user, 'teacher_profile'):
        messages.error(request, "Vous devez avoir un profil enseignant pour accéder à cette page.")
        return redirect('core:dashboard')
    
    teacher = request.user.teacher_profile
    courses = CMSUnit.objects.filter(teacher=teacher).order_by('-updated_at')[:6]  # Recent 6 courses
    
    # Calculate statistics
    stats = {
        'total_courses': CMSUnit.objects.filter(teacher=teacher).count(),
        'published_courses': CMSUnit.objects.filter(teacher=teacher, is_published=True).count(),
        'draft_courses': CMSUnit.objects.filter(teacher=teacher, is_published=False).count(),
        'synced_courses': CMSUnit.objects.filter(teacher=teacher, sync_status='synced').count(),
        'pending_sync': CMSUnit.objects.filter(teacher=teacher, sync_status='pending').count(),
        'total_chapters': sum(course.chapters.count() for course in courses),
        'total_lessons': sum(course.lessons.count() for course in courses),
    }
    
    context = {
        'teacher': teacher,
        'recent_courses': courses,
        'stats': stats,
    }
    
    return render(request, 'contentstore/dashboard.html', context)