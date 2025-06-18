"""
Tests for Jobs REST API endpoints
"""

import tempfile
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import Department, JobPosition, JobApplication


class JobAPITestCase(APITestCase):
    """Tests for Jobs API endpoints"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name="Engineering",
            description="Software development team"
        )
        
        self.position = JobPosition.objects.create(
            title="Senior Python Developer",
            department=self.department,
            location="Paris, France",
            employment_type="full_time",
            experience_level="senior",
            description="We are looking for a senior Python developer...",
            requirements="5+ years of Python experience",
            responsibilities="Develop and maintain applications",
            application_email="jobs@linguify.com"
        )
    
    def test_get_departments(self):
        """Test getting list of departments"""
        url = '/api/v1/jobs/departments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Engineering')
        self.assertIn('position_count', response.data[0])
    
    def test_get_job_positions(self):
        """Test getting list of job positions"""
        url = '/api/v1/jobs/positions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Senior Python Developer')
        self.assertEqual(response.data[0]['department_name'], 'Engineering')
        self.assertTrue(response.data[0]['is_open'])
    
    def test_get_job_positions_only_active(self):
        """Test that only active positions are returned"""
        # Create inactive position
        JobPosition.objects.create(
            title="Inactive Position",
            department=self.department,
            location="Nowhere",
            employment_type="full_time",
            experience_level="mid",
            description="Inactive position",
            requirements="None",
            responsibilities="None",
            application_email="test@linguify.com",
            is_active=False
        )
        
        url = '/api/v1/jobs/positions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only active position should be returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Senior Python Developer')
    
    def test_get_job_position_detail(self):
        """Test getting detailed information about a job position"""
        url = f'/api/v1/jobs/positions/{self.position.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Senior Python Developer')
        self.assertIn('is_open', response.data)
        self.assertIn('application_count', response.data)
        self.assertIn('department', response.data)
    
    def test_get_nonexistent_job_position(self):
        """Test getting a non-existent job position"""
        url = '/api/v1/jobs/positions/999/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_job_position_filtering_by_department(self):
        """Test filtering positions by department"""
        # Create another department and position
        marketing_dept = Department.objects.create(
            name="Marketing",
            description="Marketing team"
        )
        
        JobPosition.objects.create(
            title="Marketing Manager",
            department=marketing_dept,
            location="Lyon",
            employment_type="full_time",
            experience_level="senior",
            description="Marketing position",
            requirements="Marketing experience",
            responsibilities="Manage marketing",
            application_email="marketing@linguify.com"
        )
        
        # Filter by engineering department
        url = f'/api/v1/jobs/positions/?department={self.department.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Senior Python Developer')
    
    def test_job_position_search(self):
        """Test searching positions by title/description"""
        url = '/api/v1/jobs/positions/?search=Python'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Senior Python Developer')
        
        # Search for non-existent term
        url = '/api/v1/jobs/positions/?search=JavaScript'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_submit_application_success(self):
        """Test successful job application submission"""
        url = '/api/v1/jobs/apply/'
        data = {
            'position': self.position.id,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+33123456789',
            'cover_letter': 'I am very interested in this position...',
            'portfolio_url': 'https://johndoe.dev',
            'linkedin_url': 'https://linkedin.com/in/johndoe'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('application_id', response.data)
        
        # Verify application was created
        application = JobApplication.objects.get(id=response.data['application_id'])
        self.assertEqual(application.first_name, 'John')
        self.assertEqual(application.last_name, 'Doe')
        self.assertEqual(application.email, 'john.doe@example.com')
    
    def test_submit_application_to_closed_position(self):
        """Test submitting application to closed position"""
        # Close the position
        self.position.is_active = False
        self.position.save()
        
        url = '/api/v1/jobs/apply/'
        data = {
            'position': self.position.id,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('no longer accepting applications', response.data['error'])
    
    def test_duplicate_application_prevention(self):
        """Test prevention of duplicate applications"""
        url = '/api/v1/jobs/apply/'
        data = {
            'position': self.position.id,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com'
        }
        
        # First application
        response1 = self.client.post(url, data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Attempt duplicate application
        response2 = self.client.post(url, data)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_application_missing_required_fields(self):
        """Test application with missing required fields"""
        url = '/api/v1/jobs/apply/'
        data = {
            'position': self.position.id,
            'first_name': 'John',
            # Missing last_name and email
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_application_with_resume_file(self):
        """Test application with uploaded resume file"""
        url = '/api/v1/jobs/apply/'
        
        # Create a test PDF file
        resume_content = b'%PDF-1.4\nTest PDF content'
        resume_file = SimpleUploadedFile(
            "test_resume.pdf",
            resume_content,
            content_type="application/pdf"
        )
        
        data = {
            'position': self.position.id,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '0123456789',
            'cover_letter': 'I am interested',
            'resume_file': resume_file
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify file was saved
        application = JobApplication.objects.get(id=response.data['application_id'])
        self.assertTrue(application.resume_file)
        self.assertIn('test_resume', application.resume_file.name)
    
    def test_get_job_stats(self):
        """Test getting job statistics"""
        url = '/api/v1/jobs/stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_positions'], 1)
        self.assertEqual(response.data['departments'], 1)
        self.assertEqual(response.data['featured_positions'], 0)
        
        # Make position featured and test again
        self.position.is_featured = True
        self.position.save()
        
        response = self.client.get(url)
        self.assertEqual(response.data['featured_positions'], 1)


class JobAPIFilteringTests(APITestCase):
    """Tests for API filtering and search functionality"""
    
    def setUp(self):
        # Create multiple departments and positions
        self.eng_dept = Department.objects.create(
            name="Engineering",
            description="Software development"
        )
        
        self.marketing_dept = Department.objects.create(
            name="Marketing", 
            description="Marketing team"
        )
        
        # Engineering positions
        self.python_job = JobPosition.objects.create(
            title="Python Developer",
            department=self.eng_dept,
            location="Paris",
            employment_type="full_time",
            experience_level="mid",
            description="Python development role",
            requirements="Python skills",
            responsibilities="Code Python",
            application_email="eng@linguify.com"
        )
        
        self.js_job = JobPosition.objects.create(
            title="JavaScript Developer",
            department=self.eng_dept,
            location="Lyon",
            employment_type="contract",
            experience_level="junior",
            description="JavaScript development role",
            requirements="JS skills",
            responsibilities="Code JavaScript",
            application_email="eng@linguify.com"
        )
        
        # Marketing position
        self.marketing_job = JobPosition.objects.create(
            title="Marketing Manager",
            department=self.marketing_dept,
            location="Paris",
            employment_type="full_time",
            experience_level="senior",
            description="Marketing management role",
            requirements="Marketing experience",
            responsibilities="Manage marketing",
            application_email="marketing@linguify.com"
        )
    
    def test_filter_by_employment_type(self):
        """Test filtering by employment type"""
        url = '/api/v1/jobs/positions/?employment_type=full_time'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Python and Marketing jobs
        
        url = '/api/v1/jobs/positions/?employment_type=contract'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only JS job
        self.assertEqual(response.data[0]['title'], 'JavaScript Developer')
    
    def test_filter_by_experience_level(self):
        """Test filtering by experience level"""
        url = '/api/v1/jobs/positions/?experience_level=senior'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Marketing Manager')
    
    def test_filter_by_location(self):
        """Test filtering by location"""
        url = '/api/v1/jobs/positions/?location=Paris'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Python and Marketing jobs
    
    def test_combined_filtering(self):
        """Test combining multiple filters"""
        url = '/api/v1/jobs/positions/?department={}&employment_type=full_time'.format(
            self.eng_dept.id
        )
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only Python job
        self.assertEqual(response.data[0]['title'], 'Python Developer')
    
    def test_search_functionality(self):
        """Test search across title and description"""
        # Search in title
        url = '/api/v1/jobs/positions/?search=Python'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Developer')
        
        # Search in description
        url = '/api/v1/jobs/positions/?search=management'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Marketing Manager')