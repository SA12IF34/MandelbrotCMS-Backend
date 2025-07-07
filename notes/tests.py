from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Note
from authentication.models import Account
from sessions_manager.models import Project
from learning_tracker.models import Course
from entertainment.models import Entertainment
from goals.models import Goal
from missions.models import List


class NotesAPIsTest(TestCase):
    """Test cases for NotesAPIs view"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = Account.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create related objects        
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            user=self.user.id,
            status="in progress"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="Test course description",
            user=self.user.id,
            source="coursera",
            link="https://example.com",
            status="current",
            list=True
        )
        self.entertainment = Entertainment.objects.create(
            title="Test Entertainment",
            link="https://example.com",
            type="shows&movies",
            description=None,
            user=self.user.id,
            status="current",
            special=False
        )
        self.goal = Goal.objects.create(
            title="Test Goal",
            description="Test goal description",
            user=self.user.id,
            finish_words="Congratulations on finishing the goal"
        )
        self.missions_list = List.objects.create(
            title="Test List",
            date="2025-05-18",
            user=self.user.id
        )
        
        # Create a test file
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            b"Test file content",
            content_type="text/plain"
        )
        
        # Create the note with all relations and content types
        self.note = Note.objects.create(
            title="Test Note",
            content="Test note content",
            drawn_content="Test drawn content",
            uploaded_file=self.test_file,
            user=self.user.id,
            project=self.project,
            learning_material=self.course,
            entertainment_material=self.entertainment,
            goal=self.goal,
            missions_list=self.missions_list
        )
        self.notes_url = reverse('notes')

    def test_get_notes_success(self):
        """Test retrieving all notes successfully"""
        response = self.client.get(self.notes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_notes_unauthenticated(self):
        """Test retrieving notes without authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.notes_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_notes_with_search(self):
        """Test searching notes"""
        response = self.client.get(f"{self.notes_url}?search=Test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_get_notes_with_empty_search(self):
        """Test searching notes with empty search parameter"""
        response = self.client.get(f"{self.notes_url}?search=")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_note_success(self):
        """Test creating a note successfully with all fields"""
        test_file = SimpleUploadedFile(
            "another_test.txt",
            b"Another test file content",
            content_type="text/plain"
        )
        
        data = {
            "title": "New Note",
            "content": "New note content",
            "drawn_content": "New drawn content",
            "uploaded_file": test_file,
            "project": self.project.id,
            "learning_material": self.course.id,
            "entertainment_material": self.entertainment.id,
            "goal": self.goal.id,
            "missions_list": self.missions_list.id
        }
        response = self.client.post(self.notes_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Note')
        self.assertEqual(response.data['drawn_content'], 'New drawn content')
        self.assertTrue('uploaded_file' in response.data)

    def test_create_note_failure(self):
        """Test creating a note with invalid data"""
        data = {
            "title": "",
            "content": "",
        }
        response = self.client.post(self.notes_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class NoteAPIsTest(TestCase):
    """Test cases for NoteAPIs view"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = Account.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

        # Create related objects        
        self.project = Project.objects.create(
            title="Test Project",
            description="Test project description",
            user=self.user.id,
            status="in progress"
        )
        self.course = Course.objects.create(
            title="Test Course",
            description="Test course description",
            user=self.user.id,
            source="coursera",
            link="https://example.com",
            status="current",
            list=True
        )
        self.entertainment = Entertainment.objects.create(
            title="Test Entertainment",
            link="https://example.com",
            type="shows&movies",
            description=None,
            user=self.user.id,
            status="current",
            special=False
        )
        self.goal = Goal.objects.create(
            title="Test Goal",
            description="Test goal description",
            user=self.user.id,
            finish_words="Congratulations on finishing the goal"
        )
        self.missions_list = List.objects.create(
            title="Test List",
            date="2025-05-18",
            user=self.user.id
        )

        # Create a test file
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            b"Test file content",
            content_type="text/plain"
        )

        # Create the note with all content types and relations
        self.note = Note.objects.create(
            title="Test Note",
            content="Test note content",
            drawn_content="Test drawn content",
            uploaded_file=self.test_file,
            user=self.user.id,
            project=self.project,
            learning_material=self.course,
            entertainment_material=self.entertainment,
            goal=self.goal,
            missions_list=self.missions_list
        )
        self.note_url = reverse('note', kwargs={'pk': self.note.id})

    def test_get_note_success(self):
        """Test retrieving a single note successfully"""
        response = self.client.get(self.note_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Note')
        self.assertEqual(response.data['drawn_content'], 'Test drawn content')
        self.assertTrue('uploaded_file' in response.data)
        self.assertEqual(response.data['project'], self.project.id)
        self.assertEqual(response.data['learning_material'], self.course.id)
        self.assertEqual(response.data['entertainment_material'], self.entertainment.id)
        self.assertEqual(response.data['goal'], self.goal.id)
        self.assertEqual(response.data['missions_list'], self.missions_list.id)

    def test_get_note_not_found(self):
        """Test retrieving a non-existent note"""
        url = reverse('note', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_note_success(self):
        """Test updating a note successfully with multiple fields"""
        new_project = Project.objects.create(
            title="New Project",
            user=self.user.id
        )
        new_file = SimpleUploadedFile(
            "updated_file.txt",
            b"Updated file content",
            content_type="text/plain"
        )
        
        data = {
            "title": "Updated Title",
            "content": "Updated content",
            "drawn_content": "Updated drawn content",
            "uploaded_file": new_file,
            "project": new_project.id
        }
        response = self.client.patch(self.note_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Updated Title")
        self.assertEqual(self.note.content, "Updated content")
        self.assertEqual(self.note.drawn_content, "Updated drawn content")
        self.assertEqual(self.note.project.id, new_project.id)
        self.assertTrue(self.note.uploaded_file)

    def test_update_note_validation_errors(self):
        """Test updating a note with invalid data"""
        # Test with empty required field
        data = {
            "content": ""
        }
        response = self.client.patch(self.note_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test with invalid relationship ID
        data = {
            "project": 999  # Non-existent project ID
        }
        response = self.client.patch(self.note_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_note_success(self):
        """Test deleting a note successfully"""
        response = self.client.delete(self.note_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 0)

    def test_delete_note_not_found(self):
        """Test deleting a non-existent note"""
        url = reverse('note', kwargs={'pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
