# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from blog.profanity_filter import validate_comment_content


class Command(BaseCommand):
    help = 'Test the profanity detection system'

    def handle(self, *args, **options):
        self.stdout.write("🛡️ Testing Enhanced Profanity Detection System")
        self.stdout.write("=" * 60)
        
        # Test cases
        test_cases = [
            # Basic profanity
            ("putain de merde", "Basic French profanity"),
            ("fuck this shit", "Basic English profanity"),
            
            # Circumvention techniques
            ("put4in", "Leetspeak substitution"),
            ("f*ck", "Asterisk substitution"),
            ("p u t a i n", "Spaced letters"),
            ("putin", "Phonetic variation"),
            ("puuuutain", "Repeated vowels"),
            
            # Clean text
            ("Hello, this is a normal comment", "Clean comment"),
        ]
        
        for i, (text, description) in enumerate(test_cases, 1):
            self.stdout.write(f"\n{i}. Testing: {description}")
            self.stdout.write(f"   Input: '{text}'")
            
            result = validate_comment_content(text)
            
            if result['has_profanity']:
                if result['is_valid']:
                    status = "⚠️  WARNED"
                else:
                    status = "❌ BLOCKED"
                
                self.stdout.write(f"   Status: {status}")
                self.stdout.write(f"   Severity: {result['severity']}")
                self.stdout.write(f"   Found: {result['found_words']}")
            else:
                self.stdout.write(f"   Status: ✅ PASSED")
        
        self.stdout.write("\n🎯 Test completed!")