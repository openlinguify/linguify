# -*- coding: utf-8 -*-
"""Section views - Placeholder for now"""
from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from apps.cours.models import CourseSection


class SectionCreateView(LoginRequiredMixin, CreateView):
    model = CourseSection
    fields = ['title_fr', 'title_en', 'description_fr', 'learning_objectives']
    template_name = 'cours/section_form.html'


class SectionUpdateView(LoginRequiredMixin, UpdateView):
    model = CourseSection
    fields = ['title_fr', 'title_en', 'description_fr', 'learning_objectives']
    template_name = 'cours/section_form.html'


class SectionDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseSection
    template_name = 'cours/section_confirm_delete.html'


class SectionReorderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return HttpResponse("Reorder implemented with HTMX drag-and-drop")
