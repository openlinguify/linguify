"""
Tests for Jobs models (JobPosition, JobApplication, Department)
"""

from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError

from core.jobs.models import Department, JobPosition, JobApplication


class DepartmentModelTests(TestCase):
    """Tests for the Department model"""
    
    def test_department_creation(self):
        """Test creating a department"""
        department = Department.objects.create(
            name="Engineering",
            description="Software development team"
        )
        
        self.assertEqual(department.name, "Engineering")
        self.assertEqual(str(department), "Engineering")
        self.assertIsNotNone(department.created_at)
    
    def test_department_ordering(self):
        """Test that departments are ordered by name"""
        Department.objects.create(name="Marketing", description="Marketing team")
        Department.objects.create(name="Engineering", description="Dev team")
        Department.objects.create(name="HR", description="Human resources")
        
        departments = Department.objects.all()
        names = [dept.name for dept in departments]
        
        self.assertEqual(names, ["Engineering", "HR", "Marketing"])


class JobPositionModelTests(TestCase):
    """Tests for the JobPosition model"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team"
        )
    
    def test_job_position_creation(self):
        """Test creating a job position"""
        position = JobPosition.objects.create(
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
        
        self.assertEqual(position.title, "Python Developer")
        self.assertEqual(str(position), "Python Developer - Paris")
        self.assertTrue(position.is_active)
        self.assertIsNotNone(position.created_at)
        self.assertIsNotNone(position.posted_date)
    
    def test_job_position_is_open_when_active(self):
        """Test that an active position without closing date is open"""
        position = JobPosition.objects.create(
            title="Python Developer",
            department=self.department,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Test position",
            requirements="Python skills",
            responsibilities="Code",
            application_email="test@linguify.com",
            is_active=True
        )
        self.assertTrue(position.is_open)
    
    def test_job_position_closed_when_inactive(self):
        """Test that an inactive position is closed"""
        position = JobPosition.objects.create(
            title="Python Developer",
            department=self.department,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Test position",
            requirements="Python skills",
            responsibilities="Code",
            application_email="test@linguify.com",
            is_active=False
        )
        self.assertFalse(position.is_open)
    
    def test_job_position_closed_when_past_closing_date(self):
        """Test that a position with past closing date is closed"""
        past_date = timezone.now() - timezone.timedelta(days=1)
        position = JobPosition.objects.create(
            title="Python Developer",
            department=self.department,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Test position",
            requirements="Python skills",
            responsibilities="Code",
            application_email="test@linguify.com",
            is_active=True,
            closing_date=past_date
        )
        self.assertFalse(position.is_open)
    
    def test_job_position_open_when_future_closing_date(self):
        """Test that a position with future closing date is open"""
        future_date = timezone.now() + timezone.timedelta(days=7)
        position = JobPosition.objects.create(
            title="Python Developer",
            department=self.department,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Test position",
            requirements="Python skills",
            responsibilities="Code",
            application_email="test@linguify.com",
            is_active=True,
            closing_date=future_date
        )
        self.assertTrue(position.is_open)
    
    def test_salary_range_property(self):
        """Test the salary_range property"""
        position = JobPosition.objects.create(
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
        
        # No salary defined
        self.assertIsNone(position.salary_range)
        
        # Minimum salary only
        position.salary_min = 50000
        position.save()
        self.assertEqual(position.salary_range, "From 50,000 EUR")
        
        # Full salary range
        position.salary_max = 70000
        position.save()
        self.assertEqual(position.salary_range, "50,000 - 70,000 EUR")


class JobApplicationModelTests(TestCase):
    """Tests for the JobApplication model"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team"
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
    
    def test_job_application_creation(self):
        """Test creating a job application"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="0123456789",
            cover_letter="I'm interested in this position"
        )
        
        self.assertEqual(application.position, self.position)
        self.assertEqual(application.first_name, "John")
        self.assertEqual(application.last_name, "Doe")
        self.assertEqual(application.email, "john.doe@example.com")
        self.assertEqual(application.full_name, "John Doe")
        self.assertEqual(application.status, "submitted")
        self.assertIsNotNone(application.applied_at)
        self.assertIsNotNone(application.updated_at)
    
    def test_job_application_str_representation(self):
        """Test the string representation of a job application"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        
        expected = "Jane Smith - Python Developer"
        self.assertEqual(str(application), expected)
    
    def test_full_name_property(self):
        """Test the full_name property"""
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Jean-Claude",
            last_name="Van Damme",
            email="jcvd@example.com"
        )
        
        self.assertEqual(application.full_name, "Jean-Claude Van Damme")
    
    def test_multiple_applications_allowed(self):
        """Test that multiple applications are allowed (unique constraint removed)"""
        # First application
        JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        
        # Second application with same email should be allowed (for spontaneous applications)
        second_application = JobApplication.objects.create(
            position=self.position,
            first_name="Jane",
            last_name="Smith",
            email="john.doe@example.com"  # Same email
        )
        
        # Verify both applications exist
        self.assertEqual(JobApplication.objects.filter(email="john.doe@example.com").count(), 2)
        self.assertIsNotNone(second_application.id)
    
    def test_application_ordering(self):
        """Test that applications are ordered by applied_at descending"""
        from django.utils import timezone
        import datetime
        
        # Create applications with explicit time differences
        now = timezone.now()
        
        app1 = JobApplication.objects.create(
            position=self.position,
            first_name="First",
            last_name="User",
            email="first@example.com"
        )
        # Set an earlier time for app1
        app1.applied_at = now - datetime.timedelta(minutes=1)
        app1.save()
        
        app2 = JobApplication.objects.create(
            position=self.position,
            first_name="Second",
            last_name="User",
            email="second@example.com"
        )
        # app2 keeps the current time (more recent)
        
        applications = JobApplication.objects.all()
        
        # Most recent should be first (app2 should come before app1)
        self.assertEqual(applications[0], app2)
        self.assertEqual(applications[1], app1)
    
    def test_status_choices(self):
        """Test that all status choices are valid"""
        valid_statuses = [
            'submitted', 'reviewed', 'interview', 
            'offer', 'hired', 'rejected', 'withdrawn'
        ]
        
        application = JobApplication.objects.create(
            position=self.position,
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        
        for status in valid_statuses:
            application.status = status
            application.save()
            application.refresh_from_db()
            self.assertEqual(application.status, status)