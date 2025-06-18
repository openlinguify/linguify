# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.contrib import admin
from .models import Note, SharedNote


admin.site.register(Note)
admin.site.register(SharedNote)