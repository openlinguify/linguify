# -*- coding: utf-8 -*-
"""Pricing views"""
from django.views.generic import UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.cours.models import CoursePricing, CourseDiscount


class PricingUpdateView(LoginRequiredMixin, UpdateView):
    model = CoursePricing
    fields = ['pricing_type', 'price', 'currency', 'has_discount', 'discount_percentage']
    template_name = 'cours/pricing_form.html'


class DiscountCreateView(LoginRequiredMixin, CreateView):
    model = CourseDiscount
    fields = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_until']
    template_name = 'cours/discount_form.html'
