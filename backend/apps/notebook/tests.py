# -*- coding: utf-8 -*-
# Part of Open Linguify. See LICENSE file for full copyright and licensing details.
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from ..models import Note, NoteCategory
from core.models.tags import Tag, TagRelation
from core.models.tags import get_tags_for_object, add_tag_to_object, remove_tag_from_object

User = get_user_model()


class GlobalTagsIntegrationTest(TestCase):
    """Test integration of notebook with global tags system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create some global tags
        self.tag1 = Tag.objects.create(
            user=self.user,
            name='french',
            color='#FF5733'
        )
        self.tag2 = Tag.objects.create(
            user=self.user,
            name='grammar',
            color='#33FF57'
        )
        
        # Create a note
        self.note = Note.objects.create(
            user=self.user,
            title='Test Note',
            content='This is a test note for French grammar'
        )
    
    def test_note_can_use_global_tags(self):
        """Test that notes can use the global tag system"""
        # Add tags to note using the global system
        self.note.add_tag(self.tag1)
        self.note.add_tag(self.tag2)
        
        # Verify tags were added
        note_tags = self.note.tags
        self.assertEqual(len(note_tags), 2)
        
        tag_names = [tag.name for tag in note_tags]
        self.assertIn('french', tag_names)
        self.assertIn('grammar', tag_names)
    
    def test_note_set_tags_method(self):
        """Test the set_tags method on notes"""
        # Set tags using the set_tags method
        self.note.set_tags([self.tag1, self.tag2])
        
        # Verify tags were set
        note_tags = self.note.tags
        self.assertEqual(len(note_tags), 2)
        
        # Change tags
        new_tag = Tag.objects.create(
            user=self.user,
            name='vocabulary',
            color='#3357FF'
        )
        self.note.set_tags([new_tag])
        
        # Verify only new tag remains
        note_tags = self.note.tags
        self.assertEqual(len(note_tags), 1)
        self.assertEqual(note_tags[0].name, 'vocabulary')
    
    def test_tag_remove_method(self):
        """Test removing tags from notes"""
        # Add tags first
        self.note.add_tag(self.tag1)
        self.note.add_tag(self.tag2)
        
        # Remove one tag
        self.note.remove_tag(self.tag1)
        
        # Verify only one tag remains
        note_tags = self.note.tags
        self.assertEqual(len(note_tags), 1)
        self.assertEqual(note_tags[0].name, 'grammar')
    
    def test_tag_relations_created_correctly(self):
        """Test that TagRelations are created correctly"""
        # Add tag to note
        self.note.add_tag(self.tag1)
        
        # Check TagRelation was created
        relation = TagRelation.objects.get(
            tag=self.tag1,
            app_name='notebook',
            model_name='Note',
            object_id=str(self.note.id)
        )
        
        self.assertEqual(relation.created_by, self.user)
        self.assertEqual(relation.tag, self.tag1)
    
    def test_usage_counts_updated(self):
        """Test that usage counts are updated when tags are used"""
        initial_notebook_count = self.tag1.usage_count_notebook
        initial_total_count = self.tag1.usage_count_total
        
        # Add tag to note
        self.note.add_tag(self.tag1)
        
        # Refresh from database
        self.tag1.refresh_from_db()
        
        # Usage counts should be updated (handled by the model's recalculate method)
        # Note: This may need to be called manually in real usage
        self.tag1.recalculate_usage_counts()
        
        self.assertEqual(self.tag1.usage_count_notebook, initial_notebook_count + 1)
        self.assertEqual(self.tag1.usage_count_total, initial_total_count + 1)


class NotebookAPIWithTagsTest(APITestCase):
    """Test notebook API with global tags integration"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='apipass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create global tags
        self.tag1 = Tag.objects.create(
            user=self.user,
            name='python',
            color='#3776AB'
        )
        self.tag2 = Tag.objects.create(
            user=self.user,
            name='django',
            color='#092E20'
        )
    
    def test_create_note_with_tags_via_api(self):
        """Test creating a note with tags via the API"""
        data = {
            'title': 'Django Testing',
            'content': 'How to test Django applications',
            'tags': [str(self.tag1.id), str(self.tag2.id)]
        }
        
        response = self.client.post('/api/notebook/notes/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get the created note
        note_id = response.data['id']
        note = Note.objects.get(id=note_id)
        
        # Check tags were assigned
        note_tags = note.tags
        self.assertEqual(len(note_tags), 2)
        
        tag_names = [tag.name for tag in note_tags]
        self.assertIn('python', tag_names)
        self.assertIn('django', tag_names)
    
    def test_update_note_tags_via_api(self):
        """Test updating note tags via the API"""
        # Create a note first
        note = Note.objects.create(
            user=self.user,
            title='Original Note',
            content='Original content'
        )
        note.add_tag(self.tag1)
        
        # Update with new tags
        data = {
            'title': 'Updated Note',
            'content': 'Updated content',
            'tags': [str(self.tag2.id)]
        }
        
        response = self.client.put(f'/api/notebook/notes/{note.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check tags were updated
        note.refresh_from_db()
        note_tags = note.tags
        self.assertEqual(len(note_tags), 1)
        self.assertEqual(note_tags[0].name, 'django')
    
    def test_filter_notes_by_tags(self):
        """Test filtering notes by tags"""
        # Create notes with different tags
        note1 = Note.objects.create(
            user=self.user,
            title='Python Note',
            content='About Python'
        )
        note1.add_tag(self.tag1)
        
        note2 = Note.objects.create(
            user=self.user,
            title='Django Note',
            content='About Django'
        )
        note2.add_tag(self.tag2)
        
        note3 = Note.objects.create(
            user=self.user,
            title='Both Note',
            content='About both'
        )
        note3.add_tag(self.tag1)
        note3.add_tag(self.tag2)
        
        # Filter by python tag
        response = self.client.get('/api/notebook/notes/?tags=python')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # Should return note1 and note3
        returned_ids = [note['id'] for note in results]
        self.assertIn(note1.id, returned_ids)
        self.assertIn(note3.id, returned_ids)
        self.assertNotIn(note2.id, returned_ids)


class GlobalTagsAPITest(APITestCase):
    """Test the global tags API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='taguser',
            email='tag@example.com',
            password='tagpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_global_tag(self):
        """Test creating a global tag via API"""
        data = {
            'name': 'javascript',
            'color': '#F7DF1E',
            'description': 'JavaScript programming language'
        }
        
        response = self.client.post('/api/v1/core/tags/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify tag was created
        tag = Tag.objects.get(name='javascript', user=self.user)
        self.assertEqual(tag.color, '#F7DF1E')
        self.assertEqual(tag.description, 'JavaScript programming language')
    
    def test_list_user_tags(self):
        """Test listing user's tags"""
        # Create some tags
        Tag.objects.create(user=self.user, name='react', color='#61DAFB')
        Tag.objects.create(user=self.user, name='vue', color='#4FC08D')
        
        response = self.client.get('/api/v1/core/tags/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return user's tags only
        tag_names = [tag['name'] for tag in response.data['results']]
        self.assertIn('react', tag_names)
        self.assertIn('vue', tag_names)
    
    def test_set_object_tags_endpoint(self):
        """Test setting tags on an object via API"""
        # Create a tag and a note
        tag = Tag.objects.create(user=self.user, name='testing', color='#FF0000')
        note = Note.objects.create(
            user=self.user,
            title='Test Note',
            content='Test content'
        )
        
        data = {
            'app_name': 'notebook',
            'model_name': 'Note',
            'object_id': str(note.id),
            'tag_ids': [str(tag.id)]
        }
        
        response = self.client.post('/api/v1/core/object-tags/set_object_tags/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify tag relation was created
        relation = TagRelation.objects.get(
            tag=tag,
            app_name='notebook',
            model_name='Note',
            object_id=str(note.id)
        )
        self.assertEqual(relation.created_by, self.user)