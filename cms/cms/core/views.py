from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.cours.models import Course


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for teachers."""
    template_name = 'cms_dashboard/dashboard_modular.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get teacher
        try:
            teacher = self.request.user.teacher_profile

            # Get courses stats
            all_courses = Course.objects.filter(teacher=teacher)

            context['stats'] = {
                'total_courses': all_courses.count(),
                'published_courses': all_courses.filter(is_published=True).count(),
                'draft_courses': all_courses.filter(status='draft').count(),
                'total_students': sum(c.enrollment_count for c in all_courses),
            }

            # Recent courses
            context['recent_courses'] = all_courses.order_by('-created_at')[:6]

        except:
            context['stats'] = {
                'total_courses': 0,
                'published_courses': 0,
                'draft_courses': 0,
                'total_students': 0,
            }
            context['recent_courses'] = []

        return context