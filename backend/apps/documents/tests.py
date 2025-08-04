from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Document, Folder, DocumentShare, DocumentComment

User = get_user_model()


class DocumentModelTest(TestCase):
    """Test cases for Document model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.folder = Folder.objects.create(
            name='Test Folder',
            owner=self.user
        )
    
    def test_document_creation(self):
        """Test creating a document"""
        document = Document.objects.create(
            title='Test Document',
            content='This is test content',
            owner=self.user,
            folder=self.folder
        )
        
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.owner, self.user)
        self.assertEqual(document.folder, self.folder)
        self.assertEqual(document.content_type, 'markdown')  # default
        self.assertEqual(document.visibility, 'private')  # default
    
    def test_document_str_representation(self):
        """Test document string representation"""
        document = Document.objects.create(
            title='Test Document',
            owner=self.user
        )
        self.assertEqual(str(document), 'Test Document')
    
    def test_get_tags_list(self):
        """Test tags list parsing"""
        document = Document.objects.create(
            title='Test Document',
            owner=self.user,
            tags='python, django, test'
        )
        
        expected_tags = ['python', 'django', 'test']
        self.assertEqual(document.get_tags_list(), expected_tags)
    
    def test_empty_tags_list(self):
        """Test empty tags list"""
        document = Document.objects.create(
            title='Test Document',
            owner=self.user,
            tags=''
        )
        self.assertEqual(document.get_tags_list(), [])


class FolderModelTest(TestCase):
    """Test cases for Folder model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_folder_creation(self):
        """Test creating a folder"""
        folder = Folder.objects.create(
            name='Test Folder',
            description='Test folder description',
            owner=self.user
        )
        
        self.assertEqual(folder.name, 'Test Folder')
        self.assertEqual(folder.owner, self.user)
        self.assertEqual(folder.description, 'Test folder description')
    
    def test_folder_hierarchy(self):
        """Test folder parent-child relationship"""
        parent_folder = Folder.objects.create(
            name='Parent Folder',
            owner=self.user
        )
        
        child_folder = Folder.objects.create(
            name='Child Folder',
            owner=self.user,
            parent=parent_folder
        )
        
        self.assertEqual(child_folder.parent, parent_folder)
        self.assertIn(child_folder, parent_folder.subfolders.all())


class DocumentShareModelTest(TestCase):
    """Test cases for DocumentShare model"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collaborator@example.com',
            password='testpass123'
        )
        self.document = Document.objects.create(
            title='Shared Document',
            owner=self.owner
        )
    
    def test_document_share_creation(self):
        """Test creating a document share"""
        share = DocumentShare.objects.create(
            document=self.document,
            user=self.collaborator,
            shared_by=self.owner,
            permission_level='edit'
        )
        
        self.assertEqual(share.document, self.document)
        self.assertEqual(share.user, self.collaborator)
        self.assertEqual(share.shared_by, self.owner)
        self.assertEqual(share.permission_level, 'edit')
        self.assertFalse(share.is_expired())
    
    def test_document_share_str_representation(self):
        """Test share string representation"""
        share = DocumentShare.objects.create(
            document=self.document,
            user=self.collaborator,
            shared_by=self.owner,
            permission_level='view'
        )
        
        expected_str = f"{self.collaborator.username} - {self.document.title} (view)"
        self.assertEqual(str(share), expected_str)


class DocumentAPITest(APITestCase):
    """Test cases for Document API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_document(self):
        """Test creating document via API"""
        url = reverse('documents:document-list')
        data = {
            'title': 'API Test Document',
            'content': 'This is test content via API',
            'content_type': 'markdown'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        
        document = Document.objects.first()
        self.assertEqual(document.title, 'API Test Document')
        self.assertEqual(document.owner, self.user)
    
    def test_list_documents(self):
        """Test listing documents via API"""
        # Create test documents
        Document.objects.create(
            title='Document 1',
            owner=self.user
        )
        Document.objects.create(
            title='Document 2',
            owner=self.other_user
        )
        
        url = reverse('documents:document-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see own documents
        self.assertEqual(len(response.data['results']), 1)
    
    def test_document_detail(self):
        """Test retrieving document detail via API"""
        document = Document.objects.create(
            title='Detail Test',
            content='Detail content',
            owner=self.user
        )
        
        url = reverse('documents:document-detail', kwargs={'pk': document.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail Test')
        self.assertEqual(response.data['content'], 'Detail content')
    
    def test_update_document(self):
        """Test updating document via API"""
        document = Document.objects.create(
            title='Original Title',
            owner=self.user
        )
        
        url = reverse('documents:document-detail', kwargs={'pk': document.pk})
        data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        document.refresh_from_db()
        self.assertEqual(document.title, 'Updated Title')
        self.assertEqual(document.last_edited_by, self.user)
    
    def test_unauthorized_access(self):
        """Test accessing other user's private document"""
        document = Document.objects.create(
            title='Private Document',
            owner=self.other_user,
            visibility='private'
        )
        
        url = reverse('documents:document-detail', kwargs={'pk': document.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DocumentShareAPITest(APITestCase):
    """Test cases for Document sharing API"""
    
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collaborator@example.com',
            password='testpass123'
        )
        self.document = Document.objects.create(
            title='Shareable Document',
            owner=self.owner
        )
        self.client.force_authenticate(user=self.owner)
    
    def test_share_document(self):
        """Test sharing document via API"""
        url = reverse('documents:documentshare-list')
        data = {
            'document': self.document.pk,
            'user_id': self.collaborator.pk,
            'permission_level': 'edit'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check share was created
        share = DocumentShare.objects.get(
            document=self.document,
            user=self.collaborator
        )
        self.assertEqual(share.permission_level, 'edit')
        self.assertEqual(share.shared_by, self.owner)
    
    def test_shared_document_access(self):
        """Test that shared document is accessible to collaborator"""
        # Create share
        DocumentShare.objects.create(
            document=self.document,
            user=self.collaborator,
            shared_by=self.owner,
            permission_level='view'
        )
        
        # Switch to collaborator
        self.client.force_authenticate(user=self.collaborator)
        
        # Try to access document
        url = reverse('documents:document-detail', kwargs={'pk': self.document.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Shareable Document')


class WebViewTest(TestCase):
    """Test cases for web views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_main_view(self):
        """Test main documents view"""
        url = reverse('documents:main')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Documents')
    
    def test_document_list_view(self):
        """Test document list view"""
        Document.objects.create(
            title='Test Document',
            owner=self.user
        )
        
        url = reverse('documents:document_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Document')
    
    def test_document_create_view(self):
        """Test document creation view"""
        url = reverse('documents:document_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'title': 'New Document',
            'content': 'New content',
            'content_type': 'markdown',
            'visibility': 'private'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        
        # Verify document was created
        document = Document.objects.get(title='New Document')
        self.assertEqual(document.owner, self.user)