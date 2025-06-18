from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Remove default value from TheoryContent.content_lesson field'

    def handle(self, *args, **options):
        self.stdout.write("=== Removing default from TheoryContent.content_lesson ===")
        
        # Check current default
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'course_theorycontent' 
                AND column_name = 'content_lesson_id'
            """)
            result = cursor.fetchone()
            if result:
                self.stdout.write(f"Current default: {result[0]}")
            
            # Remove the default
            try:
                cursor.execute("""
                    ALTER TABLE course_theorycontent 
                    ALTER COLUMN content_lesson_id DROP DEFAULT
                """)
                self.stdout.write(self.style.SUCCESS("Default removed successfully"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to remove default: {e}"))