# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

# URLs for terms and conditions

from django.urls import path
from ..views.terms_views import terms_acceptance_view, accept_terms_ajax, terms_status_web, accept_terms_web

urlpatterns = [
    path('accept/', terms_acceptance_view, name='terms_acceptance'),
    path('accept/ajax/', accept_terms_ajax, name='accept_terms_ajax'),
    path('status/', terms_status_web, name='terms_status'),
    path('accept/web/', accept_terms_web, name='accept_terms_web'),
]