from django.core.management.base import BaseCommand
from django.db import transaction
import json
import os
from apps.course.models import ContentLesson, VocabularyList

class Command(BaseCommand):
    help = 'Insert clothing vocabulary into ContentLesson 160'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== CLOTHING VOCABULARY INSERTION ==='))
        
        # Load the JSON data
        json_file_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'clothing_vocabulary.json')
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('ERROR: clothing_vocabulary.json not found!')
            )
            return
        
        self.stdout.write(f"Loaded {len(data['vocabulary_words'])} vocabulary words from JSON")
        
        # Get the ContentLesson
        try:
            content_lesson = ContentLesson.objects.get(id=160)
            self.stdout.write(f"Found ContentLesson: {content_lesson}")
        except ContentLesson.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('ERROR: ContentLesson with ID 160 not found!')
            )
            return
        
        # Check if vocabulary already exists
        existing_vocab = VocabularyList.objects.filter(content_lesson=content_lesson)
        if existing_vocab.exists():
            self.stdout.write(
                self.style.WARNING(f'Warning: {existing_vocab.count()} vocabulary words already exist for this lesson.')
            )
            confirm = input("Do you want to delete existing vocabulary and add new ones? (y/n): ")
            if confirm.lower() == 'y':
                existing_vocab.delete()
                self.stdout.write(self.style.SUCCESS("Existing vocabulary deleted."))
            else:
                self.stdout.write("Operation cancelled.")
                return
        
        # Insert vocabulary words in a transaction
        vocabulary_words = data['vocabulary_words']
        created_count = 0
        
        self.stdout.write(f"\nInserting {len(vocabulary_words)} vocabulary words...")
        
        try:
            with transaction.atomic():
                for word_data in vocabulary_words:
                    vocabulary = VocabularyList.objects.create(
                        content_lesson=content_lesson,
                        word_en=word_data['word_en'],
                        word_fr=word_data['word_fr'],
                        word_es=word_data['word_es'],
                        word_nl=word_data['word_nl'],
                        definition_en=word_data['definition_en'],
                        definition_fr=word_data['definition_fr'],
                        definition_es=word_data['definition_es'],
                        definition_nl=word_data['definition_nl'],
                        word_type_en=word_data['word_type_en'],
                        word_type_fr=word_data['word_type_fr'],
                        word_type_es=word_data['word_type_es'],
                        word_type_nl=word_data['word_type_nl'],
                        example_sentence_en=word_data['example_sentence_en'],
                        example_sentence_fr=word_data['example_sentence_fr'],
                        example_sentence_es=word_data['example_sentence_es'],
                        example_sentence_nl=word_data['example_sentence_nl'],
                        synonymous_en=word_data.get('synonymous_en', ''),
                        synonymous_fr=word_data.get('synonymous_fr', ''),
                        synonymous_es=word_data.get('synonymous_es', ''),
                        synonymous_nl=word_data.get('synonymous_nl', ''),
                        antonymous_en=word_data.get('antonymous_en', ''),
                        antonymous_fr=word_data.get('antonymous_fr', ''),
                        antonymous_es=word_data.get('antonymous_es', ''),
                        antonymous_nl=word_data.get('antonymous_nl', '')
                    )
                    created_count += 1
                    self.stdout.write(
                        f"✓ Created: {word_data['word_en']} / {word_data['word_fr']} / {word_data['word_es']} / {word_data['word_nl']}"
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'ERROR during insertion: {e}')
            )
            return
        
        # Summary
        self.stdout.write(f"\n=== SUMMARY ===")
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} vocabulary words")
        )
        
        final_count = VocabularyList.objects.filter(content_lesson=content_lesson).count()
        self.stdout.write(
            self.style.SUCCESS(f"ContentLesson 160 now has {final_count} vocabulary words")
        )
        
        # Verification
        self.stdout.write(f"\n=== VERIFICATION ===")
        final_vocab = VocabularyList.objects.filter(content_lesson=content_lesson).order_by('id')
        for i, vocab in enumerate(final_vocab, 1):
            self.stdout.write(f"{i:2d}. {vocab.word_en:12s} / {vocab.word_fr:15s} / {vocab.word_es:18s} / {vocab.word_nl}")
        
        self.stdout.write(
            self.style.SUCCESS('\n=== CLOTHING VOCABULARY INSERTION COMPLETED ===')
        )