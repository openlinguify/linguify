from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PrivateLesson

class CalendarView(LoginRequiredMixin, TemplateView):
    """Teacher calendar view."""
    template_name = 'scheduling/calendar.html'

class LessonListView(LoginRequiredMixin, ListView):
    """List teacher's private lessons."""
    model = PrivateLesson
    template_name = 'scheduling/lessons.html'
    paginate_by = 20
    
    def get_queryset(self):
        return PrivateLesson.objects.filter(teacher__user=self.request.user)

class AvailabilityView(LoginRequiredMixin, TemplateView):
    """Manage teacher availability."""
    template_name = 'scheduling/availability.html'