# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path
from django import forms
from .models import Lesson, ContentLesson, TheoryContent
import json

class TheoryContentBulkForm(forms.Form):
    """Form for bulk creating theory content"""
    lessons = forms.ModelMultipleChoiceField(
        queryset=Lesson.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Lessons"
    )
    
    title_en = forms.CharField(max_length=255, label="Title (English)")
    title_fr = forms.CharField(max_length=255, label="Title (French)")
    title_es = forms.CharField(max_length=255, label="Title (Spanish)")  
    title_nl = forms.CharField(max_length=255, label="Title (Dutch)")
    
    template = forms.ChoiceField(
        choices=[
            ('custom', 'Custom Content'),
            ('dates', 'Dates Template'),
            ('plurals', 'Plurals Template'),
            ('time', 'Time Template'),
            ('numbers', 'Numbers Template')
        ],
        initial='custom'
    )
    
    json_content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 20, 'cols': 80, 'placeholder': '{\n  "en": {\n    "content": "",\n    "explanation": ""\n  }\n}'}),
        required=False,
        label="JSON Content (for custom template)"
    )

def add_theory_content_actions(admin_site):
    """Add custom actions to the admin site"""
    
    def bulk_create_theory_view(request):
        if request.method == 'POST':
            form = TheoryContentBulkForm(request.POST)
            if form.is_valid():
                lessons = form.cleaned_data['lessons']
                template = form.cleaned_data['template']
                
                # Get content based on template
                if template == 'custom':
                    try:
                        content = json.loads(form.cleaned_data['json_content'])
                    except json.JSONDecodeError:
                        messages.error(request, "Invalid JSON content")
                        return render(request, 'admin/course/bulk_create_theory.html', {'form': form})
                else:
                    content = get_template_content(template)
                
                created_count = 0
                for lesson in lessons:
                    # Check if Theory ContentLesson already exists
                    existing = ContentLesson.objects.filter(
                        lesson=lesson,
                        content_type='Theory',
                        title_en=form.cleaned_data['title_en']
                    ).first()
                    
                    if not existing:
                        # Get next order
                        max_order = ContentLesson.objects.filter(lesson=lesson).order_by('-order').first()
                        order = (max_order.order + 1) if max_order else 1
                        
                        # Create ContentLesson
                        content_lesson = ContentLesson.objects.create(
                            lesson=lesson,
                            content_type='Theory',
                            title_en=form.cleaned_data['title_en'],
                            title_fr=form.cleaned_data['title_fr'],
                            title_es=form.cleaned_data['title_es'],
                            title_nl=form.cleaned_data['title_nl'],
                            order=order,
                            estimated_duration=15
                        )
                        
                        # Create TheoryContent
                        TheoryContent.objects.create(
                            content_lesson=content_lesson,
                            using_json_format=True,
                            language_specific_content=content,
                            available_languages=list(content.keys()),
                            **extract_traditional_fields(content)
                        )
                        
                        created_count += 1
                
                messages.success(request, f"Created {created_count} theory lessons")
                return redirect('admin:course_contentlesson_changelist')
        else:
            form = TheoryContentBulkForm()
        
        return render(request, 'admin/course/bulk_create_theory.html', {
            'form': form,
            'title': 'Bulk Create Theory Content'
        })
    
    # Register the URL
    admin_site.urls.append(
        path('course/theory/bulk-create/', bulk_create_theory_view, name='bulk_create_theory'),
    )
    
    return bulk_create_theory_view

def get_template_content(template_name):
    """Get predefined template content"""
    templates = {
        'dates': {
            "en": {
                "content": "Learning dates in English: days, months, and formats",
                "explanation": "Dates can be written in different formats",
                "example": "January 15, 2024 or 15/01/2024",
                "formula": "Month Day, Year or DD/MM/YYYY"
            },
            "fr": {
                "content": "Apprendre les dates en français : jours, mois et formats",
                "explanation": "Les dates peuvent s'écrire de différentes façons",
                "example": "15 janvier 2024 ou 15/01/2024",
                "formula": "Jour Mois Année ou JJ/MM/AAAA"
            },
            "es": {
                "content": "Aprender las fechas en español: días, meses y formatos",
                "explanation": "Las fechas se pueden escribir de diferentes formas",
                "example": "15 de enero de 2024 o 15/01/2024",
                "formula": "Día de Mes de Año o DD/MM/AAAA"
            },
            "nl": {
                "content": "Datums leren in het Nederlands: dagen, maanden en formaten",
                "explanation": "Datums kunnen op verschillende manieren worden geschreven",
                "example": "15 januari 2024 of 15-01-2024",
                "formula": "Dag Maand Jaar of DD-MM-JJJJ"
            }
        },
        'time': {
            "en": {"content": "Time expressions", "explanation": "How to tell time"},
            "fr": {"content": "Les expressions temporelles", "explanation": "Comment dire l'heure"},
            "es": {"content": "Las expresiones de tiempo", "explanation": "Cómo decir la hora"},
            "nl": {"content": "Tijdsuitdrukkingen", "explanation": "Hoe je de tijd zegt"}
        },
        'plurals': {
            "en": {"content": "Plural forms", "explanation": "How to form plurals"},
            "fr": {"content": "Les formes plurielles", "explanation": "Comment former le pluriel"},
            "es": {"content": "Las formas plurales", "explanation": "Cómo formar el plural"},
            "nl": {"content": "Meervoudsvormen", "explanation": "Hoe meervouden te vormen"}
        },
        'numbers': {
            "en": {"content": "Numbers and counting", "explanation": "Cardinal and ordinal numbers"},
            "fr": {"content": "Les nombres", "explanation": "Nombres cardinaux et ordinaux"},
            "es": {"content": "Los números", "explanation": "Números cardinales y ordinales"},
            "nl": {"content": "Getallen", "explanation": "Hoofdtelwoorden en rangtelwoorden"}
        }
    }
    return templates.get(template_name, {})

def extract_traditional_fields(content):
    """Extract traditional fields from JSON content"""
    fields = {}
    for lang in ['en', 'fr', 'es', 'nl']:
        if lang in content:
            fields[f'content_{lang}'] = content[lang].get('content', '')
            fields[f'explication_{lang}'] = content[lang].get('explanation', '')
            fields[f'formula_{lang}'] = content[lang].get('formula', '')
            fields[f'example_{lang}'] = content[lang].get('example', '')
            fields[f'exception_{lang}'] = content[lang].get('exception', '')
    return fields