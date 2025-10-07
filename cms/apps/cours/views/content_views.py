# -*- coding: utf-8 -*-
"""Content views - Placeholder"""
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.cours.models import CourseContent


class ContentCreateView(LoginRequiredMixin, CreateView):
    model = CourseContent
    fields = ['title', 'content_type', 'text_content']
    template_name = 'cours/content_form.html'


class ContentUpdateView(LoginRequiredMixin, UpdateView):
    model = CourseContent
    fields = ['title', 'content_type', 'text_content']
    template_name = 'cours/content_form.html'


class ContentDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseContent
    template_name = 'cours/content_confirm_delete.html'
