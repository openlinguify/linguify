# -*- coding: utf-8 -*-
"""Lesson views - Placeholder for now"""
from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from apps.cours.models import CourseLesson


class LessonCreateView(LoginRequiredMixin, CreateView):
    model = CourseLesson
    fields = ['title_fr', 'description_fr', 'lesson_type', 'duration_minutes']
    template_name = 'cours/lesson_form.html'


class LessonUpdateView(LoginRequiredMixin, UpdateView):
    model = CourseLesson
    fields = ['title_fr', 'description_fr', 'lesson_type', 'duration_minutes']
    template_name = 'cours/lesson_form.html'


class LessonDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseLesson
    template_name = 'cours/lesson_confirm_delete.html'


class LessonReorderView(LoginRequiredMixin, View):
    def post(self, request, lesson_id):
        return HttpResponse("Reorder implemented with HTMX")
