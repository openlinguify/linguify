# -*- coding: utf-8 -*-
"""
Course views with HTMX support
"""
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Count, Avg

from apps.cours.models import Course, CourseSection
from apps.teachers.models import Teacher


class HTMXMixin:
    """Mixin to detect HTMX requests and adjust template response."""

    def get_template_names(self):
        """Return partial template for HTMX requests."""
        if self.request.htmx:
            # Return partial template for HTMX
            return [self.htmx_template_name]
        return [self.template_name]


class CourseListView(LoginRequiredMixin, HTMXMixin, ListView):
    """List all courses for the logged-in teacher."""
    model = Course
    template_name = 'cours/course_list.html'
    htmx_template_name = 'cours/partials/course_list_partial.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        """Get courses for the current teacher."""
        # Get teacher profile
        try:
            teacher = self.request.user.teacher_profile
        except:
            return Course.objects.none()

        queryset = Course.objects.filter(
            Q(teacher=teacher) | Q(co_instructors=teacher)
        ).distinct()

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title_fr__icontains=search) |
                Q(title_en__icontains=search) |
                Q(description_fr__icontains=search)
            )

        # Order by
        order_by = self.request.GET.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)

        return queryset.annotate(
            section_count=Count('sections'),
            lesson_count=Count('lessons')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    """Create a new course."""
    model = Course
    template_name = 'cours/course_form.html'
    fields = [
        'title_fr', 'subtitle_fr', 'description_fr',
        'title_en', 'subtitle_en', 'description_en',
        'category', 'tags', 'level', 'language',
        'learning_objectives', 'requirements', 'target_audience',
        'thumbnail', 'promo_video'
    ]

    def form_valid(self, form):
        """Set the teacher to the current user."""
        try:
            form.instance.teacher = self.request.user.teacher_profile
        except:
            messages.error(self.request, "You must be a teacher to create courses.")
            return redirect('cours:course_list')

        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cours:course_detail', kwargs={'slug': self.object.slug})


class CourseDetailView(LoginRequiredMixin, DetailView):
    """Display course details with curriculum builder."""
    model = Course
    template_name = 'cours/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get sections with lessons
        sections = self.object.sections.prefetch_related('lessons').order_by('order')
        context['sections'] = sections

        # Statistics
        context['total_sections'] = sections.count()
        context['total_lessons'] = self.object.lessons.count()
        context['total_students'] = self.object.enrollment_count

        # Check permissions
        try:
            teacher = self.request.user.teacher_profile
            context['can_edit'] = (
                self.object.teacher == teacher or
                teacher in self.object.co_instructors.all()
            )
        except:
            context['can_edit'] = False

        return context


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    """Update course details."""
    model = Course
    template_name = 'cours/course_form.html'
    fields = [
        'title_fr', 'subtitle_fr', 'description_fr',
        'title_en', 'subtitle_en', 'description_en',
        'category', 'tags', 'level', 'language',
        'learning_objectives', 'requirements', 'target_audience',
        'thumbnail', 'promo_video',
        'is_enrollable', 'max_students',
        'has_certificate', 'has_lifetime_access'
    ]

    def get_queryset(self):
        """Only allow teacher to edit their own courses."""
        try:
            teacher = self.request.user.teacher_profile
            return Course.objects.filter(
                Q(teacher=teacher) | Q(co_instructors=teacher)
            ).distinct()
        except:
            return Course.objects.none()

    def form_valid(self, form):
        messages.success(self.request, "Course updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cours:course_detail', kwargs={'slug': self.object.slug})


class CourseDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a course."""
    model = Course
    template_name = 'cours/course_confirm_delete.html'
    success_url = reverse_lazy('cours:course_list')

    def get_queryset(self):
        """Only allow teacher to delete their own courses."""
        try:
            teacher = self.request.user.teacher_profile
            return Course.objects.filter(teacher=teacher)
        except:
            return Course.objects.none()

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Course deleted successfully!")
        return super().delete(request, *args, **kwargs)


class CoursePublishView(LoginRequiredMixin, View):
    """Publish/unpublish a course (HTMX)."""

    def post(self, request, slug):
        """Toggle course publish status."""
        try:
            teacher = request.user.teacher_profile
            course = get_object_or_404(
                Course,
                Q(teacher=teacher) | Q(co_instructors=teacher),
                slug=slug
            )

            action = request.POST.get('action')

            if action == 'publish':
                course.publish()
                messages.success(request, f"'{course.title}' has been published!")
            elif action == 'unpublish':
                course.unpublish()
                messages.success(request, f"'{course.title}' has been unpublished!")

            # Return updated status badge for HTMX
            if request.htmx:
                return render(request, 'cours/partials/course_status_badge.html', {
                    'course': course
                })

            return redirect('cours:course_detail', slug=course.slug)

        except:
            messages.error(request, "You don't have permission to publish this course.")
            return redirect('cours:course_list')
