from django.core.management.base import BaseCommand
from django.db import transaction
from apps.course.models import ContentLesson, TheoryContent, Lesson
import json
import os

class Command(BaseCommand):
    help = 'Bulk create theory lessons from a configuration file'

    def add_arguments(self, parser):
        parser.add_argument('--config', type=str, required=True, help='Path to JSON configuration file')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating')
        
    def handle(self, *args, **options):
        config_file = options['config']
        dry_run = options['dry_run']
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.stdout.write(f"Processing {len(config.get('lessons', []))} theory lessons...")
        
        for lesson_config in config.get('lessons', []):
            try:
                self.process_lesson(lesson_config, dry_run)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing lesson: {e}"))
    
    def process_lesson(self, config, dry_run):
        lesson_id = config.get('lesson_id')
        title = config.get('title')
        content_file = config.get('content_file')
        order = config.get('order')
        template = config.get('template')
        
        lesson = Lesson.objects.get(id=lesson_id)
        
        # Check if already exists
        existing = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='Theory',
            title_en=title
        ).exists()
        
        if existing:
            self.stdout.write(f"Theory lesson '{title}' already exists in {lesson}")
            return
        
        # Load content
        if content_file and os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                theory_content = json.load(f)
        elif template:
            theory_content = self.get_template_content(template)
        else:
            self.stdout.write(self.style.WARNING(f"No content source for '{title}'"))
            return
        
        if dry_run:
            self.stdout.write(f"Would create: {title} in {lesson} (order: {order})")
            return
        
        with transaction.atomic():
            # Create ContentLesson
            content_lesson = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Theory',
                title_en=title,
                title_fr=config.get('title_fr', title),
                title_es=config.get('title_es', title),
                title_nl=config.get('title_nl', title),
                order=order or self.get_next_order(lesson),
                estimated_duration=config.get('duration', 15)
            )
            
            # Create TheoryContent
            theory = TheoryContent.objects.create(
                content_lesson=content_lesson,
                using_json_format=True,
                language_specific_content=theory_content,
                available_languages=list(theory_content.keys()),
                **self.extract_traditional_fields(theory_content)
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created: {title} (CL:{content_lesson.id}, TC:{theory.id})"))
    
    def get_next_order(self, lesson):
        max_order = ContentLesson.objects.filter(lesson=lesson).order_by('-order').first()
        return (max_order.order + 1) if max_order else 1
    
    def extract_traditional_fields(self, content):
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
    
    def get_template_content(self, template_name):
        """Get predefined templates"""
        templates = {
            'dates': {
                "en": {"content": "Dates in English", "explanation": "Date formats explanation"},
                "fr": {"content": "Les dates en français", "explanation": "Explication des formats"},
                "es": {"content": "Las fechas en español", "explanation": "Explicación de formatos"},
                "nl": {"content": "Datums in het Nederlands", "explanation": "Uitleg van formaten"}
            },
            'time': {
                "en": {"content": "Time expressions", "explanation": "How to tell time"},
                "fr": {"content": "L'heure", "explanation": "Comment dire l'heure"},
                "es": {"content": "La hora", "explanation": "Cómo decir la hora"},
                "nl": {"content": "De tijd", "explanation": "Hoe je de tijd zegt"}
            }
        }
        return templates.get(template_name, {})