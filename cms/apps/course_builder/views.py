from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import CMSUnit, CMSChapter, CMSLesson
from apps.teachers.models import Teacher

class TeacherRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user is a teacher."""
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            from django.contrib import messages
            messages.error(request, "Vous devez avoir un profil enseignant pour accéder à cette page.")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class CourseListView(TeacherRequiredMixin, ListView):
    """List teacher's courses (units)."""
    model = CMSUnit
    template_name = 'course_builder/course_list.html'
    context_object_name = 'units'
    paginate_by = 10
    
    def get_queryset(self):
        return CMSUnit.objects.filter(teacher=self.request.user.teacher_profile)

class CourseCreateView(TeacherRequiredMixin, CreateView):
    """Create new course."""
    model = CMSUnit
    template_name = 'course_builder/course_create.html'
    fields = ['title_en', 'title_fr', 'title_es', 'title_nl', 
              'description_en', 'description_fr', 'description_es', 'description_nl',
              'level', 'price']
    success_url = reverse_lazy('course_builder:course_list')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        return super().form_valid(form)

class CourseDetailView(TeacherRequiredMixin, DetailView):
    """Course detail view."""
    model = CMSUnit
    template_name = 'course_builder/course_detail.html'
    context_object_name = 'unit'
    
    def get_queryset(self):
        return CMSUnit.objects.filter(teacher=self.request.user.teacher_profile)

class CourseEditView(TeacherRequiredMixin, UpdateView):
    """Edit course."""
    model = CMSUnit
    template_name = 'course_builder/course_edit.html'
    fields = ['title_en', 'title_fr', 'title_es', 'title_nl', 
              'description_en', 'description_fr', 'description_es', 'description_nl',
              'level', 'price', 'is_published']
    
    def get_queryset(self):
        return CMSUnit.objects.filter(teacher=self.request.user.teacher_profile)
    
    def get_success_url(self):
        return reverse_lazy('course_builder:course_detail', kwargs={'pk': self.object.pk})

class ChapterListView(TeacherRequiredMixin, ListView):
    """List chapters for a course."""
    model = CMSChapter
    template_name = 'course_builder/chapter_list.html'
    context_object_name = 'chapters'
    
    def get_queryset(self):
        unit = get_object_or_404(CMSUnit, pk=self.kwargs['pk'], teacher=self.request.user.teacher_profile)
        return CMSChapter.objects.filter(unit=unit)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit'] = get_object_or_404(CMSUnit, pk=self.kwargs['pk'], teacher=self.request.user.teacher_profile)
        return context

class LessonListView(TeacherRequiredMixin, ListView):
    """List lessons for a course."""
    model = CMSLesson
    template_name = 'course_builder/lesson_list.html'
    context_object_name = 'lessons'
    
    def get_queryset(self):
        unit = get_object_or_404(CMSUnit, pk=self.kwargs['pk'], teacher=self.request.user.teacher_profile)
        return CMSLesson.objects.filter(unit=unit)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unit'] = get_object_or_404(CMSUnit, pk=self.kwargs['pk'], teacher=self.request.user.teacher_profile)
        return context