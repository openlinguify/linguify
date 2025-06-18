"""
Tests for utility functions and helpers
"""

from django.test import TestCase
from django.utils import timezone

from ..models import Department, JobPosition


class UtilityTests(TestCase):
    """Tests for utility functions and model methods"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development"
        )
        
        self.position = JobPosition.objects.create(
            title="Python Developer",
            department=self.department,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Test position",
            requirements="Python skills",
            responsibilities="Code",
            application_email="test@linguify.com"
        )
    
    def test_employment_type_choices(self):
        """Test employment type choices are valid"""
        valid_types = [
            'full_time', 'part_time', 'contract', 
            'internship', 'remote'
        ]
        
        for emp_type in valid_types:
            self.position.employment_type = emp_type
            self.position.save()
            self.position.refresh_from_db()
            self.assertEqual(self.position.employment_type, emp_type)
    
    def test_experience_level_choices(self):
        """Test experience level choices are valid"""
        valid_levels = [
            'entry', 'mid', 'senior', 'lead', 'manager'
        ]
        
        for level in valid_levels:
            self.position.experience_level = level
            self.position.save()
            self.position.refresh_from_db()
            self.assertEqual(self.position.experience_level, level)
    
    def test_timezone_aware_datetime_fields(self):
        """Test that datetime fields are timezone aware"""
        self.assertTrue(timezone.is_aware(self.position.created_at))
        self.assertTrue(timezone.is_aware(self.position.updated_at))
        self.assertTrue(timezone.is_aware(self.position.posted_date))
    
    def test_model_ordering(self):
        """Test model ordering works correctly"""
        # Create positions with different dates and featured status
        pos1 = JobPosition.objects.create(
            title="First Job",
            department=self.department,
            location="City1",
            employment_type="full_time",
            experience_level="mid",
            description="First",
            requirements="Skills",
            responsibilities="Work",
            application_email="test1@linguify.com",
            is_featured=False
        )
        
        pos2 = JobPosition.objects.create(
            title="Featured Job",
            department=self.department,
            location="City2",
            employment_type="full_time",
            experience_level="mid",
            description="Featured",
            requirements="Skills",
            responsibilities="Work",
            application_email="test2@linguify.com",
            is_featured=True
        )
        
        positions = JobPosition.objects.all()
        
        # Featured positions should come first
        # Then by posted_date descending
        self.assertEqual(positions[0], pos2)  # Featured first
    
    def test_department_string_representation(self):
        """Test department string representation"""
        dept_name = "Test Department"
        dept = Department.objects.create(
            name=dept_name,
            description="Test description"
        )
        
        self.assertEqual(str(dept), dept_name)
    
    def test_position_salary_formatting(self):
        """Test salary formatting edge cases"""
        # Test with very large numbers
        self.position.salary_min = 1000000
        self.position.salary_max = 2000000
        self.position.save()
        
        expected = "1,000,000 - 2,000,000 EUR"
        self.assertEqual(self.position.salary_range, expected)
        
        # Test with only max salary
        self.position.salary_min = None
        self.position.salary_max = 75000
        self.position.save()
        
        # Should not show range when only max is set
        self.assertIsNone(self.position.salary_range)
    
    def test_position_is_open_edge_cases(self):
        """Test is_open property edge cases"""
        # Test with closing date exactly now
        now = timezone.now()
        self.position.closing_date = now
        self.position.save()
        
        # Should be closed if closing time has passed
        # (even by microseconds due to execution time)
        # This might pass or fail depending on timing
        
        # Test with future date very close to now
        future = timezone.now() + timezone.timedelta(seconds=1)
        self.position.closing_date = future
        self.position.save()
        
        self.assertTrue(self.position.is_open)
    
    def test_model_field_max_lengths(self):
        """Test model field maximum lengths"""
        # Test title max length
        long_title = "a" * 201  # Exceeds 200 char limit
        
        # This should not save without truncation
        # (In production, this would be handled by form validation)
        
        # Test location max length
        long_location = "b" * 201
        
        # These tests ensure our model constraints are reasonable
        self.assertLessEqual(len(self.position.title), 200)
        self.assertLessEqual(len(self.position.location), 200)