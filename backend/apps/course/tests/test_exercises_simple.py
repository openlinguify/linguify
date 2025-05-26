# -*- coding: utf-8 -*-
# Part of Linguify. See LICENSE file for full copyright and licensing details.

import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestCourseBasics:
    """Simple tests to verify pytest configuration with Django."""
    
    def test_django_db_setup(self):
        """Simple test to check that the database connection works."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Create a test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        # Check that the user was created
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        
        # Delete the user
        user.delete()
        assert User.objects.filter(username='testuser').count() == 0
        
    def test_timezone_awareness(self):
        """Test to verify that dates are handled with timezone awareness."""
        now = timezone.now()
        assert now.tzinfo is not None
        
        # Check that the date is in the future
        future = now + timezone.timedelta(days=30)
        assert future > now
        
        # Check that the difference is 30 days
        diff = future - now
        assert diff.days == 30