import logging
from django.core.management.base import BaseCommand
from apps.course.models import ContentLesson, TestRecap

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Shows the relationship between a content lesson and test recaps'

    def add_arguments(self, parser):
        parser.add_argument(
            'content_lesson_id',
            type=int,
            help='ID of the content lesson to check'
        )

    def handle(self, *args, **options):
        content_lesson_id = options['content_lesson_id']
        
        try:
            # Get the content lesson
            cl = ContentLesson.objects.get(id=content_lesson_id)
            self.stdout.write(f'Content Lesson {content_lesson_id}:')
            self.stdout.write(f'  Title: {cl.title_en}')
            self.stdout.write(f'  Type: {cl.content_type}')
            
            # Check if it has a parent lesson
            if cl.lesson:
                parent_lesson_id = cl.lesson.id
                self.stdout.write(f'  Parent Lesson ID: {parent_lesson_id}')
                self.stdout.write(f'  Parent Lesson Title: {cl.lesson.title_en}')
                
                # Check for test recaps associated with the parent lesson
                test_recaps = TestRecap.objects.filter(lesson_id=parent_lesson_id)
                
                if test_recaps.exists():
                    self.stdout.write(f'  Found {test_recaps.count()} test recap(s) associated with parent lesson:')
                    for i, tr in enumerate(test_recaps, 1):
                        self.stdout.write(f'    {i}. Test Recap ID: {tr.id}')
                        self.stdout.write(f'       Title: {tr.title}')
                        
                        # Show question count
                        questions = tr.questions.all()
                        self.stdout.write(f'       Questions: {questions.count()}')
                        
                        # Check for questions without content
                        missing_content = 0
                        for q in questions:
                            has_content = (
                                q.multiple_choice_id or
                                q.fill_blank_id or
                                q.matching_id or
                                q.reordering_id or
                                q.speaking_id or
                                q.vocabulary_id
                            )
                            if not has_content:
                                missing_content += 1
                        
                        if missing_content > 0:
                            self.stdout.write(f'       WARNING: {missing_content} questions have no content!')
                else:
                    self.stdout.write(f'  No test recaps found for parent lesson {parent_lesson_id}')
            else:
                self.stdout.write(f'  WARNING: Content lesson has no parent lesson!')
                
        except ContentLesson.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Content lesson with ID {content_lesson_id} not found'))