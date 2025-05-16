"""
Management command to fix the TestRecap table schema inconsistencies.
Run with: python manage.py fix_testrecap_schema
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fixes TestRecap table schema inconsistencies between the title and title_* fields"

    def handle(self, *args, **options):
        self.stdout.write("Examining TestRecap table schema...")
        
        # First check the schema to understand what we're working with
        check_schema_sql = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'course_testrecap' 
        ORDER BY column_name;
        """
        
        with connection.cursor() as cursor:
            cursor.execute(check_schema_sql)
            columns = cursor.fetchall()
            
            self.stdout.write("\nCurrent TestRecap table columns:")
            for column in columns:
                self.stdout.write(f"- {column[0]}: {column[1]} {'' if column[2] == 'YES' else '(NOT NULL)'}")
        
        # Determine if we need to copy title_* to title or add title column
        has_title = any(column[0] == 'title' for column in columns)
        has_title_en = any(column[0] == 'title_en' for column in columns)
        has_question = any(column[0] == 'question' for column in columns)
        
        # SQL to fix the column issues
        fix_title_sql = ""
        fix_question_sql = ""
        
        if has_title and has_title_en:
            # Both fields exist, copy title_en to title
            fix_title_sql = """
            -- Copy values from title_en to title where title is NULL
            UPDATE course_testrecap 
            SET title = title_en 
            WHERE title IS NULL;
            """
            self.stdout.write("\nBoth 'title' and 'title_en' columns exist. Will copy title_en values to title.")
            
        elif has_title and not has_title_en:
            # Only title exists, add title_* columns and copy from title
            fix_title_sql = """
            -- Add missing title_* columns if they don't exist
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'course_testrecap' 
                    AND column_name = 'title_en'
                ) THEN
                    ALTER TABLE course_testrecap ADD COLUMN title_en VARCHAR(255);
                    ALTER TABLE course_testrecap ADD COLUMN title_fr VARCHAR(255);
                    ALTER TABLE course_testrecap ADD COLUMN title_es VARCHAR(255);
                    ALTER TABLE course_testrecap ADD COLUMN title_nl VARCHAR(255);
                    
                    -- Copy title to all language-specific fields
                    UPDATE course_testrecap SET 
                        title_en = title, 
                        title_fr = title, 
                        title_es = title, 
                        title_nl = title;
                        
                    RAISE NOTICE 'Added title_* columns and copied data from title';
                END IF;
            END $$;
            """
            self.stdout.write("\nOnly 'title' column exists. Will add title_* columns and copy from title.")
            
        elif not has_title and has_title_en:
            # Only title_* exist, add title column and copy from title_en
            fix_title_sql = """
            -- Add title column
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'course_testrecap' 
                    AND column_name = 'title'
                ) THEN
                    ALTER TABLE course_testrecap ADD COLUMN title VARCHAR(255);
                    
                    -- Copy title_en to title
                    UPDATE course_testrecap SET title = title_en;
                    
                    -- Make title NOT NULL
                    ALTER TABLE course_testrecap ALTER COLUMN title SET NOT NULL;
                    
                    RAISE NOTICE 'Added title column and copied data from title_en';
                END IF;
            END $$;
            """
            self.stdout.write("\nOnly title_* columns exist. Will add title column and copy from title_en.")
            
        else:
            # Neither exist, add both
            fix_title_sql = """
            -- Add all missing title columns
            DO $$
            BEGIN
                -- Add title column
                ALTER TABLE course_testrecap ADD COLUMN title VARCHAR(255) DEFAULT 'Default Title' NOT NULL;
                
                -- Add title_* columns
                ALTER TABLE course_testrecap ADD COLUMN title_en VARCHAR(255) DEFAULT 'Default Title';
                ALTER TABLE course_testrecap ADD COLUMN title_fr VARCHAR(255) DEFAULT 'Titre par défaut';
                ALTER TABLE course_testrecap ADD COLUMN title_es VARCHAR(255) DEFAULT 'Título predeterminado';
                ALTER TABLE course_testrecap ADD COLUMN title_nl VARCHAR(255) DEFAULT 'Standaard titel';
                
                RAISE NOTICE 'Added all title columns with default values';
            END $$;
            """
            self.stdout.write("\nNeither title nor title_* columns exist. Will add all with default values.")
        
        # Handle question field
        if not has_question and has_title_en:
            fix_question_sql = """
            -- Add question column if it doesn't exist
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'course_testrecap' 
                    AND column_name = 'question'
                ) THEN
                    ALTER TABLE course_testrecap ADD COLUMN question VARCHAR(255);
                    
                    -- Copy title_en to question
                    UPDATE course_testrecap SET question = title_en;
                    
                    -- Make question NOT NULL
                    ALTER TABLE course_testrecap ALTER COLUMN question SET NOT NULL;
                    
                    RAISE NOTICE 'Added question column and copied data from title_en';
                END IF;
            END $$;
            """
            self.stdout.write("\nThe 'question' column is missing. Will add it and copy from title_en.")
        elif not has_question and has_title:
            fix_question_sql = """
            -- Add question column if it doesn't exist
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'course_testrecap' 
                    AND column_name = 'question'
                ) THEN
                    ALTER TABLE course_testrecap ADD COLUMN question VARCHAR(255);
                    
                    -- Copy title to question
                    UPDATE course_testrecap SET question = title;
                    
                    -- Make question NOT NULL
                    ALTER TABLE course_testrecap ALTER COLUMN question SET NOT NULL;
                    
                    RAISE NOTICE 'Added question column and copied data from title';
                END IF;
            END $$;
            """
            self.stdout.write("\nThe 'question' column is missing. Will add it and copy from title.")
        
        # Execute the SQL to fix the columns
        has_changes = False
        
        if fix_title_sql:
            with connection.cursor() as cursor:
                self.stdout.write("\nApplying title field fixes...")
                cursor.execute(fix_title_sql)
            has_changes = True
        
        if fix_question_sql:
            with connection.cursor() as cursor:
                self.stdout.write("\nApplying question field fixes...")
                cursor.execute(fix_question_sql)
            has_changes = True
            
        # Check the updated schema
        if has_changes:
            with connection.cursor() as cursor:
                cursor.execute(check_schema_sql)
                columns = cursor.fetchall()
                
                self.stdout.write("\nUpdated TestRecap table columns:")
                for column in columns:
                    self.stdout.write(f"- {column[0]}: {column[1]} {'' if column[2] == 'YES' else '(NOT NULL)'}")
                    
            self.stdout.write(self.style.SUCCESS("\nFixes applied successfully!"))
            self.stdout.write(self.style.SUCCESS("Now you should be able to create TestRecap entries in the admin."))
        else:
            self.stdout.write("\nNo fixes needed!")