from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from apps.course.models import MatchingExercise, ContentLesson, VocabularyList

class Command(BaseCommand):
    help = "List all matching exercises that may need updating"
    
    def handle(self, *args, **options):
        self.stdout.write("\nAnalyzing Matching Exercises...\n" + "=" * 50 + "\n")
        
        issues = []
        
        for exercise in MatchingExercise.objects.all().select_related('content_lesson__lesson'):
            lesson = exercise.content_lesson.lesson
            
            # Find associated vocabulary
            vocab_count = self._get_vocabulary_count(exercise)
            
            issue_data = {
                'exercise': exercise,
                'lesson': lesson,
                'vocab_count': vocab_count,
                'pairs_count': exercise.pairs_count,
                'issues': []
            }
            
            # Check for issues
            if vocab_count == 0:
                issue_data['issues'].append('No vocabulary found')
            elif vocab_count > 8 and exercise.pairs_count == 8:
                issue_data['issues'].append(f'Limited to 8 pairs but has {vocab_count} vocabulary items')
            elif vocab_count > exercise.pairs_count:
                issue_data['issues'].append(f'Vocabulary ({vocab_count}) exceeds pairs ({exercise.pairs_count})')
            
            if issue_data['issues']:
                issues.append(issue_data)
        
        # Display results
        if not issues:
            self.stdout.write(self.style.SUCCESS("No issues found!"))
            return
        
        self.stdout.write(f"Found {len(issues)} exercises with potential issues:\n")
        
        for data in issues:
            self.stdout.write(f"\nLesson: {data['lesson'].title_en} (ID: {data['lesson'].id})")
            self.stdout.write(f"Exercise: {data['exercise'].title_en or data['exercise'].title_fr}")
            self.stdout.write(f"Vocabulary: {data['vocab_count']} items")
            self.stdout.write(f"Pairs: {data['pairs_count']}")
            self.stdout.write(self.style.WARNING("Issues:"))
            for issue in data['issues']:
                self.stdout.write(f"  - {issue}")
            
            # Suggest fix
            if data['vocab_count'] > 8:
                num_exercises = (data['vocab_count'] + 4) // 5  # 5 pairs per exercise
                self.stdout.write(self.style.SUCCESS(
                    f"\nSuggested fix: Delete and recreate with split\n"
                    f"poetry run python manage.py matching_commands create --lesson-id {data['lesson'].id} --split --pairs-per-exercise 5\n"
                    f"This will create {num_exercises} exercises of 5 pairs each"
                ))
        
        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(f"\nTotal exercises with issues: {len(issues)}")
        
        # Quick fix command
        self.stdout.write("\nTo fix all issues automatically:")
        self.stdout.write(self.style.SUCCESS(
            "poetry run python manage.py update_all_matching_exercises --pairs-per-exercise 5"
        ))
    
    def _get_vocabulary_count(self, exercise):
        """Get total vocabulary count for an exercise"""
        if hasattr(exercise, 'vocabulary_lists'):
            return sum(v.vocabularyitem_set.count() for v in exercise.vocabulary_lists.all())
        
        # Try through lesson
        lesson = exercise.content_lesson.lesson
        vocab_contents = ContentLesson.objects.filter(
            lesson=lesson,
            content_type='vocabulary'
        )
        
        total = 0
        for content in vocab_contents:
            vocab_lists = VocabularyList.objects.filter(content_lesson=content)
            total += sum(v.vocabularyitem_set.count() for v in vocab_lists)
        
        return total