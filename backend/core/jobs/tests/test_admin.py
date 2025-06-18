"""
Tests for Django admin interface functionality
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Department, JobPosition, JobApplication
from ..admin import JobPositionAdmin, JobApplicationAdmin, DepartmentAdmin

User = get_user_model()


class AdminInterfaceTests(TestCase):
    """Tests for admin interface setup and access"""
    
    def setUp(self):
        # Create superuser for admin access
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)
        
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
    
    def test_admin_access_requires_authentication(self):
        """Test that admin requires authentication"""
        self.client.logout()
        
        url = reverse('admin:jobs_jobposition_changelist')
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_admin_models_are_registered(self):
        """Test that all models are registered in admin"""
        url = reverse('admin:index')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jobs and Careers")
        self.assertContains(response, "Departments")
        self.assertContains(response, "Job positions")
        self.assertContains(response, "Job applications")


class JobPositionAdminTests(TestCase):
    """Tests for JobPosition admin interface"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)
        
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
    
    def test_job_position_list_display(self):
        """Test job position list view displays correctly"""
        url = reverse('admin:jobs_jobposition_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")
        self.assertContains(response, "Engineering")
        self.assertContains(response, "Paris")
    
    def test_job_position_detail_view(self):
        """Test job position detail view"""
        url = reverse('admin:jobs_jobposition_change', args=[self.position.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Developer")
        
        # Check fieldset sections are present
        self.assertContains(response, "Basic Information")
        self.assertContains(response, "Job Details")
        self.assertContains(response, "Salary Information")
        self.assertContains(response, "Application Settings")
        self.assertContains(response, "Status &amp; Dates")
    
    def test_status_badge_open_position(self):
        """Test status badge for open position"""
        admin = JobPositionAdmin(JobPosition, None)
        
        badge_html = admin.status_badge(self.position)
        self.assertIn("Open", badge_html)
        self.assertIn("blue", badge_html)
    
    def test_status_badge_featured_position(self):
        """Test status badge for featured position"""
        self.position.is_featured = True
        self.position.save()
        
        admin = JobPositionAdmin(JobPosition, None)
        badge_html = admin.status_badge(self.position)
        
        self.assertIn("Featured &amp; Open", badge_html)
        self.assertIn("green", badge_html)
    
    def test_status_badge_closed_position(self):
        """Test status badge for closed position"""
        self.position.is_active = False
        self.position.save()
        
        admin = JobPositionAdmin(JobPosition, None)
        badge_html = admin.status_badge(self.position)
        
        self.assertIn("Inactive", badge_html)
        self.assertIn("red", badge_html)
    
    def test_status_badge_deadline_passed(self):
        """Test status badge for position with passed deadline"""
        past_date = timezone.now() - timezone.timedelta(days=1)
        self.position.closing_date = past_date
        self.position.save()
        
        admin = JobPositionAdmin(JobPosition, None)
        badge_html = admin.status_badge(self.position)
        
        self.assertIn("Closed", badge_html)
        self.assertIn("deadline passed", badge_html)
        self.assertIn("red", badge_html)
    
    def test_application_count_display(self):
        """Test application count display"""
        # Create test applications
        JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        JobApplication.objects.create(
            position=self.position,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        
        admin = JobPositionAdmin(JobPosition, None)
        count_html = admin.application_count(self.position)
        
        self.assertIn("2 applications", count_html)
        self.assertIn('<a href=', count_html)  # Should be a link
    
    def test_application_count_detail_with_statuses(self):
        """Test detailed application count by status"""
        JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            status="submitted"
        )
        
        JobApplication.objects.create(
            position=self.position,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            status="reviewed"
        )
        
        admin = JobPositionAdmin(JobPosition, None)
        detail = admin.application_count_detail(self.position)
        
        self.assertIn("Total: 2", detail)
        self.assertIn("Submitted: 1", detail)
        self.assertIn("Reviewed: 1", detail)
    
    def test_admin_actions_available(self):
        """Test that admin actions are available"""
        url = reverse('admin:jobs_jobposition_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Check action dropdown is present
        self.assertContains(response, 'name="action"')
    
    def test_closing_date_help_text(self):
        """Test that closing date has helpful description"""
        url = reverse('admin:jobs_jobposition_change', args=[self.position.id])
        response = self.client.get(url)
        
        # Check help text for closing date
        self.assertContains(response, "Set closing_date to prevent new applications")
        self.assertContains(response, "Leave empty for indefinite applications")


class JobApplicationAdminTests(TestCase):
    """Tests for JobApplication admin interface"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)
        
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
        
        self.application = JobApplication.objects.create(
            position=self.position,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="0123456789",
            cover_letter="I am interested in this position"
        )
    
    def test_job_application_list_display(self):
        """Test job application list view"""
        url = reverse('admin:jobs_jobapplication_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "john.doe@example.com")
        self.assertContains(response, "Python Developer")
    
    def test_job_application_detail_view(self):
        """Test job application detail view"""
        url = reverse('admin:jobs_jobapplication_change', args=[self.application.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John")
        self.assertContains(response, "Doe")
        self.assertContains(response, "john.doe@example.com")
        self.assertContains(response, "0123456789")
        self.assertContains(response, "I am interested in this position")
        
        # Check fieldset sections
        self.assertContains(response, "Application Details")
        self.assertContains(response, "Applicant Information")
        self.assertContains(response, "Application Materials")
        self.assertContains(response, "Internal Notes")
    
    def test_resume_file_field_displayed(self):
        """Test that resume_file field is displayed in admin"""
        url = reverse('admin:jobs_jobapplication_change', args=[self.application.id])
        response = self.client.get(url)
        
        self.assertContains(response, "Resume file")
        self.assertContains(response, "Resume url")
    
    def test_application_status_badge(self):
        """Test status badge for applications"""
        admin = JobApplicationAdmin(JobApplication, None)
        
        # Test submitted status
        badge_html = admin.status_badge(self.application)
        self.assertIn("Submitted", badge_html)
        self.assertIn("blue", badge_html)
        
        # Test reviewed status
        self.application.status = "reviewed"
        self.application.save()
        
        badge_html = admin.status_badge(self.application)
        self.assertIn("Under Review", badge_html)
        self.assertIn("orange", badge_html)
    
    def test_bulk_actions_work(self):
        """Test bulk actions in admin"""
        # Create another application
        application2 = JobApplication.objects.create(
            position=self.position,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            status="submitted"
        )
        
        url = reverse('admin:jobs_jobapplication_changelist')
        
        # Test mark_reviewed action
        response = self.client.post(url, {
            'action': 'mark_reviewed',
            '_selected_action': [self.application.id, application2.id],
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after action
        
        # Check statuses were updated
        self.application.refresh_from_db()
        application2.refresh_from_db()
        
        self.assertEqual(self.application.status, 'reviewed')
        self.assertEqual(application2.status, 'reviewed')
    
    def test_application_inline_in_position_admin(self):
        """Test that applications appear as inline in position admin"""
        url = reverse('admin:jobs_jobposition_change', args=[self.position.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Check inline is present
        self.assertContains(response, "John Doe")
        self.assertContains(response, "john.doe@example.com")


class DepartmentAdminTests(TestCase):
    """Tests for Department admin interface"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)
        
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team"
        )
        
        # Create positions to test counting
        JobPosition.objects.create(
            title="Python Developer",
            department=self.department,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Test position",
            requirements="Python",
            responsibilities="Code",
            application_email="test@linguify.com"
        )
        
        JobPosition.objects.create(
            title="JavaScript Developer",
            department=self.department,
            location="Lyon",
            employment_type="full_time",
            experience_level="junior",
            description="JS position",
            requirements="JavaScript",
            responsibilities="Code JS",
            application_email="test@linguify.com"
        )
    
    def test_department_list_display(self):
        """Test department list view"""
        url = reverse('admin:jobs_department_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Engineering")
    
    def test_department_position_count_display(self):
        """Test that position count is displayed"""
        url = reverse('admin:jobs_department_changelist')
        response = self.client.get(url)
        
        # Should show position count as a link
        self.assertContains(response, "2 active positions")
        self.assertContains(response, '<a href=')
    
    def test_position_count_method(self):
        """Test the position_count admin method"""
        admin = DepartmentAdmin(Department, None)
        count_html = admin.position_count(self.department)
        
        self.assertIn('<a href=', count_html)
        self.assertIn('department__id__exact=', count_html)
        self.assertIn('2 active positions', count_html)
    
    def test_position_count_zero(self):
        """Test position count display when no positions"""
        empty_dept = Department.objects.create(
            name="Empty Department",
            description="No positions"
        )
        
        admin = DepartmentAdmin(Department, None)
        count_html = admin.position_count(empty_dept)
        
        self.assertEqual(count_html, '0 positions')


class AdminFilteringTests(TestCase):
    """Tests for admin filtering and search functionality"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password123'
        )
        
        self.client = Client()
        self.client.force_login(self.admin_user)
        
        # Create test data
        self.eng_dept = Department.objects.create(
            name="Engineering",
            description="Dev team"
        )
        
        self.marketing_dept = Department.objects.create(
            name="Marketing",
            description="Marketing team"
        )
        
        self.position1 = JobPosition.objects.create(
            title="Senior Python Developer",
            department=self.eng_dept,
            location="Paris",
            employment_type="full_time",
            experience_level="senior",
            description="Python role",
            requirements="Python",
            responsibilities="Code",
            application_email="test@linguify.com",
            is_featured=True
        )
        
        self.position2 = JobPosition.objects.create(
            title="Marketing Manager",
            department=self.marketing_dept,
            location="Lyon",
            employment_type="part_time",
            experience_level="mid",
            description="Marketing role",
            requirements="Marketing",
            responsibilities="Manage",
            application_email="marketing@linguify.com"
        )
    
    def test_position_filtering_by_department(self):
        """Test filtering positions by department"""
        url = reverse('admin:jobs_jobposition_changelist')
        response = self.client.get(url + f'?department__id__exact={self.eng_dept.id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Developer")
        self.assertNotContains(response, "Marketing Manager")
    
    def test_position_filtering_by_featured(self):
        """Test filtering positions by featured status"""
        url = reverse('admin:jobs_jobposition_changelist')
        response = self.client.get(url + '?is_featured__exact=1')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Developer")
        self.assertNotContains(response, "Marketing Manager")
    
    def test_position_search_functionality(self):
        """Test search functionality in admin"""
        url = reverse('admin:jobs_jobposition_changelist')
        response = self.client.get(url + '?q=Python')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Developer")
        self.assertNotContains(response, "Marketing Manager")
    
    def test_application_filtering_by_status(self):
        """Test filtering applications by status"""
        # Create applications with different statuses
        JobApplication.objects.create(
            position=self.position1,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            status="submitted"
        )
        
        JobApplication.objects.create(
            position=self.position2,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            status="reviewed"
        )
        
        url = reverse('admin:jobs_jobapplication_changelist')
        response = self.client.get(url + '?status__exact=submitted')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")