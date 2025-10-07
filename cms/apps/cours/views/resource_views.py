# -*- coding: utf-8 -*-
"""Resource views"""
from django.views.generic import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.cours.models import CourseResource


class ResourceUploadView(LoginRequiredMixin, CreateView):
    model = CourseResource
    fields = ['title', 'description', 'resource_type', 'file', 'external_link']
    template_name = 'cours/resource_form.html'


class ResourceDeleteView(LoginRequiredMixin, DeleteView):
    model = CourseResource
    template_name = 'cours/resource_confirm_delete.html'
