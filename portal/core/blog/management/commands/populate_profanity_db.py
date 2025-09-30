# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from core.blog.models import ProfanityWord


class Command(BaseCommand):
    help = 'Populate profanity database from secure configuration file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config-file',
            type=str,
            help='Path to JSON configuration file containing profanity words',
            required=False
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing profanity words before importing',
        )

    def handle(self, *args, **options):
        config_file = options.get('config_file')
        clear_existing = options.get('clear_existing', False)

        if clear_existing:
            self.stdout.write('Clearing existing profanity words...')
            ProfanityWord.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing words cleared.'))

        if config_file:
            self.load_from_config_file(config_file)
        else:
            self.load_minimal_words()

        # Clear cache after update
        from core.blog.profanity_filter import profanity_filter
        profanity_filter.clear_cache()
        
        self.stdout.write(self.style.SUCCESS('Profanity database populated successfully.'))

    def load_from_config_file(self, config_file):
        """Load profanity words from external JSON configuration file"""
        if not os.path.exists(config_file):
            self.stdout.write(self.style.ERROR(f'Configuration file not found: {config_file}'))
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.stdout.write(f'Loading profanity words from {config_file}...')
            self.create_words_from_data(data)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading configuration file: {e}'))

    def load_minimal_words(self):
        """Load minimal set of profanity words for basic protection"""
        self.stdout.write('Loading minimal profanity word set...')
        
        minimal_data = {
            'en': {
                'mild': ['spam', 'junk'],
                'moderate': ['damn', 'crap'],
                'severe': ['offensive', 'abuse']
            },
            'fr': {
                'mild': ['spam'],
                'moderate': ['zut'],
                'severe': ['abuse']
            },
            'es': {
                'mild': ['spam'],
                'moderate': ['tonto'],
                'severe': ['abuse']
            },
            'nl': {
                'mild': ['spam'],
                'moderate': ['stom'],
                'severe': ['abuse']
            }
        }
        
        self.create_words_from_data(minimal_data)

    @transaction.atomic
    def create_words_from_data(self, data):
        """Create ProfanityWord objects from structured data"""
        valid_languages = [choice[0] for choice in ProfanityWord.LANGUAGE_CHOICES]
        valid_severities = [choice[0] for choice in ProfanityWord.SEVERITY_CHOICES]
        created_count = 0
        
        for language, severity_groups in data.items():
            if language not in valid_languages:
                self.stdout.write(self.style.WARNING(f'Skipping unsupported language: {language}'))
                continue
                
            for severity, words in severity_groups.items():
                if severity not in valid_severities:
                    self.stdout.write(self.style.WARNING(f'Skipping invalid severity: {severity}'))
                    continue
                
                for word in words:
                    if not word or not isinstance(word, str):
                        continue
                        
                    word_clean = word.strip().lower()
                    if len(word_clean) < 2:  # Skip very short words
                        continue
                    
                    try:
                        obj, created = ProfanityWord.objects.get_or_create(
                            word=word_clean,
                            language=language,
                            defaults={
                                'severity': severity,
                                'is_active': True
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            # Update existing word if needed
                            if obj.severity != severity:
                                obj.severity = severity
                                obj.save(update_fields=['severity'])
                                
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Error creating word "{word_clean}" ({language}): {e}'
                            )
                        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} new profanity words.')
        )

    def get_sample_config(self):
        """Return sample configuration structure for reference"""
        return {
            "en": {
                "mild": ["word1", "word2"],
                "moderate": ["word3", "word4"],
                "severe": ["word5", "word6"]
            },
            "fr": {
                "mild": ["mot1", "mot2"],
                "moderate": ["mot3", "mot4"],
                "severe": ["mot5", "mot6"]
            }
        }