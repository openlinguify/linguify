# -*- coding: utf-8 -*-
"""Review views"""
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.cours.models import CourseReview


class ReviewListView(LoginRequiredMixin, ListView):
    model = CourseReview
    template_name = 'cours/review_list.html'
    context_object_name = 'reviews'


class ReviewModerateView(LoginRequiredMixin, UpdateView):
    model = CourseReview
    fields = ['is_published']
    template_name = 'cours/review_moderate.html'
