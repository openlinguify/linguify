# Simple test to verify the test infrastructure works

from django.test import TestCase


class SimpleTest(TestCase):
    """Simple test to verify test infrastructure"""
    
    def test_simple_assertion(self):
        """Test that basic assertions work"""
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_django_available(self):
        """Test that Django is properly available"""
        from django.conf import settings
        self.assertIsNotNone(settings)