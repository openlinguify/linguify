from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Teacher

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
              'phone_number', 'country', 'city', 'hourly_rate']
    
    def get_object(self):
        return get_object_or_404(Teacher, user=self.request.user)