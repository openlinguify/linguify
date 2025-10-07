# -*- coding: utf-8 -*-
"""Enrollment views"""
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.cours.models import CourseEnrollment


class EnrollmentListView(LoginRequiredMixin, ListView):
    model = CourseEnrollment
    template_name = 'cours/enrollment_list.html'
    context_object_name = 'enrollments'


class EnrollmentStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'cours/enrollment_stats.html'
