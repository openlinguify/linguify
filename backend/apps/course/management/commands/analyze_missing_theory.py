from django.core.management.base import BaseCommand
from apps.course.models import Lesson, ContentLesson, TheoryContent, Unit
from django.db.models import Count, Q
import re

class Command(BaseCommand):
    help = 'Analyze lessons to find where theory content is missing'

    def add_arguments(self, parser):
        parser.add_argument('--unit', type=int, help='Filter by specific unit')
        parser.add_argument('--create', action='store_true', help='Automatically create missing theory content')
        parser.add_argument('--report', action='store_true', help='Generate detailed report')
        parser.add_argument('--check-duplicates', action='store_true', help='Check for duplicate theories')
        parser.add_argument('--dry-run', action='store_true', help='Preview what would be created')
        
    def handle(self, *args, **options):
        unit_filter = options.get('unit')
        auto_create = options.get('create')
        show_report = options.get('report')
        check_duplicates = options.get('check_duplicates')
        dry_run = options.get('dry_run')
        
        # Check for duplicates if requested
        if check_duplicates:
            self.check_duplicate_theories()
            return
        
        # Show detailed report if requested
        if show_report:
            self.generate_report()
            return
        
        # Get lessons
        lessons = Lesson.objects.all()
        if unit_filter:
            lessons = lessons.filter(unit_id=unit_filter)
        
        lessons = lessons.order_by('unit__order', 'order')
        
        self.stdout.write("=== Analyzing Lessons for Missing Theory Content ===\n")
        
        missing_theory = []
        created_count = 0
        
        for lesson in lessons:
            # Check if lesson has any theory content
            # Check both 'Theory' and 'theory' to handle case issues
            has_theory = ContentLesson.objects.filter(
                lesson=lesson,
                content_type__iexact='Theory'  # Case-insensitive check
            ).exists()
            
            if not has_theory:
                # Analyze if this lesson should have theory
                if self.should_have_theory(lesson):
                    topic = self.extract_topic(lesson)
                    template = self.suggest_template(lesson, topic)
                    
                    missing_theory.append({
                        'lesson': lesson,
                        'topic': topic,
                        'template': template
                    })
                    
                    self.stdout.write(
                        f"Missing theory in: {lesson.title_en}\n"
                        f"  Suggested title: {topic}\n"
                        f"  Suggested template: {template}\n"
                    )
                    
                    if auto_create:
                        try:
                            self.create_theory_content(lesson, topic, template)
                            created_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Failed to create: {e}"))
        
        # Summary
        self.stdout.write(f"\n=== Summary ===")
        self.stdout.write(f"Total lessons analyzed: {lessons.count()}")
        
        if auto_create:
            self.stdout.write(f"Theory content created: {created_count}")
            # Recount missing after creation
            final_missing = 0
            for lesson in lessons:
                has_theory = ContentLesson.objects.filter(
                    lesson=lesson,
                    content_type__iexact='Theory'
                ).exists()
                if not has_theory and self.should_have_theory(lesson):
                    final_missing += 1
            self.stdout.write(f"Still missing theory content: {final_missing}")
        else:
            self.stdout.write(f"Missing theory content: {len(missing_theory)}")
        
        if missing_theory and not auto_create:
            self.stdout.write("\nTo automatically create missing theory content, run with --create flag")
    
    def should_have_theory(self, lesson):
        """Determine if a lesson should have theory content"""
        title_lower = lesson.title_en.lower()
        
        # Grammar lessons should have theory
        if 'grammar' in title_lower:
            return True
        
        # Check for specific topics that usually need theory
        theory_topics = [
            'article', 'plural', 'conjugation', 'tense', 'pronoun',
            'preposition', 'adjective', 'adverb', 'passive', 'conditional',
            'subjunctive', 'imperative', 'gerund', 'participle'
        ]
        
        for topic in theory_topics:
            if topic in title_lower:
                return True
        
        # Check if lesson already has complex content that might need theory
        has_complex = ContentLesson.objects.filter(
            lesson=lesson,
            content_type__in=['Reordering', 'Grammar']
        ).exists()
        
        return has_complex
    
    def extract_topic(self, lesson):
        """Extract topic from lesson title"""
        title = lesson.title_en
        
        # Remove unit prefix
        title = re.sub(r'^Unit \d+\s*-\s*', '', title)
        
        # Extract main topic (before type indicator)
        match = re.search(r'^(.+?)\s*-\s*(grammar|vocabulary|lesson|review)?\s*$', title, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return title.strip()
    
    def suggest_template(self, lesson, topic):
        """Suggest appropriate template based on topic"""
        topic_lower = topic.lower()
        title_lower = lesson.title_en.lower()
        
        # Direct mappings
        template_map = {
            'articles': 'articles',
            'article': 'articles',
            'plural': 'plurals',
            'plurals': 'plurals',
            'time': 'time',
            'hour': 'time',
            'dates': 'dates',
            'date': 'dates',
            'day': 'dates',
            'month': 'dates',
            'number': 'numbers',
            'counting': 'numbers',
            'present simple': 'tenses',
            'past simple': 'tenses',
            'future': 'tenses',
            'present continuous': 'tenses',
            'perfect': 'tenses',
            'conditional': 'conditional',
            'subjunctive': 'subjunctive',
            'passive': 'passive',
            'pronoun': 'pronouns',
            'preposition': 'prepositions',
            'adjective': 'adjectives',
            'adverb': 'adverbs',
        }
        
        # Check for direct match
        for keyword, template in template_map.items():
            if keyword in topic_lower or keyword in title_lower:
                return template
        
        # Grammar lessons get generic grammar template
        if 'grammar' in title_lower:
            return 'grammar'
        
        return 'generic'
    
    def create_theory_content(self, lesson, topic, template):
        """Create theory content for the lesson"""
        try:
            from apps.course.management.commands.create_smart_theory_lesson import Command as SmartCommand
            
            smart_cmd = SmartCommand()
            
            # Get next order
            max_order = ContentLesson.objects.filter(lesson=lesson).order_by('-order').first()
            order = (max_order.order + 1) if max_order else 1
            
            # Create content lesson
            content_lesson = ContentLesson.objects.create(
                lesson=lesson,
                content_type='Theory',
                title_en=topic,
                title_fr=smart_cmd.translate_title(topic, 'fr'),
                title_es=smart_cmd.translate_title(topic, 'es'),
                title_nl=smart_cmd.translate_title(topic, 'nl'),
                order=order,
                estimated_duration=15
            )
            
            # Get template content
            theory_content = smart_cmd.get_template_content(template, topic)
            
            # Create theory content
            theory = TheoryContent.objects.create(
                content_lesson=content_lesson,
                using_json_format=True,
                language_specific_content=theory_content,
                available_languages=list(theory_content.keys()),
                **smart_cmd.extract_traditional_fields(theory_content)
            )
            
            self.stdout.write(self.style.SUCCESS(f"Created theory content: {content_lesson}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create theory for {lesson}: {e}"))
    
    def check_duplicate_theories(self):
        """Check for lessons with duplicate theory content"""
        self.stdout.write("=== Checking for Duplicate Theories ===\n")
        
        lessons_with_duplicates = Lesson.objects.annotate(
            theory_count=Count('content_lessons', filter=Q(content_lessons__content_type='Theory'))
        ).filter(theory_count__gt=1)
        
        if not lessons_with_duplicates.exists():
            self.stdout.write(self.style.SUCCESS("No duplicate theories found!"))
            return
        
        self.stdout.write(self.style.WARNING(f"Found {lessons_with_duplicates.count()} lessons with duplicate theories:\n"))
        
        for lesson in lessons_with_duplicates:
            self.stdout.write(f"Lesson: {lesson.title_en} (ID: {lesson.id})")
            self.stdout.write(f"  Number of theories: {lesson.theory_count}")
            
            theories = ContentLesson.objects.filter(
                lesson=lesson,
                content_type='Theory'
            ).order_by('id')
            
            for theory in theories:
                self.stdout.write(f"  - ID: {theory.id}, Title: {theory.title_en}, Order: {theory.order}")
        
        self.stdout.write("\nTo fix duplicates, use: python scripts/find_duplicate_theories.py")
    
    def generate_report(self):
        """Generate detailed report on theory content status"""
        self.stdout.write("=== Theory Content Report ===\n")
        
        # Global stats
        total_lessons = Lesson.objects.count()
        lessons_with_theory = Lesson.objects.filter(
            content_lessons__content_type='Theory'
        ).distinct().count()
        total_theories = ContentLesson.objects.filter(content_type='Theory').count()
        
        self.stdout.write("Global Statistics:")
        self.stdout.write(f"  Total lessons: {total_lessons}")
        self.stdout.write(f"  Lessons with theory: {lessons_with_theory}")
        self.stdout.write(f"  Total theories: {total_theories}")
        self.stdout.write(f"  Coverage: {lessons_with_theory/total_lessons*100:.1f}%")
        
        # By unit
        self.stdout.write("\nBreakdown by Unit:")
        units = Unit.objects.all().order_by('order')
        
        for unit in units:
            lessons_in_unit = Lesson.objects.filter(unit=unit)
            with_theory = lessons_in_unit.filter(
                content_lessons__content_type='Theory'
            ).distinct().count()
            
            self.stdout.write(f"\nUnit {unit.order}: {unit.title_en}")
            self.stdout.write(f"  Lessons: {lessons_in_unit.count()}")
            self.stdout.write(f"  With theory: {with_theory}")
            if lessons_in_unit.count() > 0:
                self.stdout.write(f"  Coverage: {with_theory/lessons_in_unit.count()*100:.1f}%")
            else:
                self.stdout.write(f"  Coverage: N/A (no lessons)")
        
        # Check for issues
        self.stdout.write("\nPotential Issues:")
        
        # Duplicates
        duplicates = Lesson.objects.annotate(
            theory_count=Count('content_lessons', filter=Q(content_lessons__content_type='Theory'))
        ).filter(theory_count__gt=1).count()
        
        if duplicates > 0:
            self.stdout.write(self.style.WARNING(f"  - {duplicates} lessons with duplicate theories"))
        
        # Missing theories
        missing = Lesson.objects.exclude(
            content_lessons__content_type='Theory'
        ).count()
        
        if missing > 0:
            self.stdout.write(self.style.WARNING(f"  - {missing} lessons without theory"))