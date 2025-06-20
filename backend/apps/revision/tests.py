# revision/tests.py
"""
Tests for the revision app
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class RevisionTestCase(TestCase):
    """Basic test case for revision app"""
    
    def test_revision_app_loads(self):
        """Test that the revision app loads without errors"""
        from apps.revision import models
        from apps.revision import serializers
        from apps.revision import views
        
        # If we get here without import errors, the test passes
        self.assertTrue(True)
