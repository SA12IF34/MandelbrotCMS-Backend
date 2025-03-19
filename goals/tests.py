from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Goal
from authentication.models import Account

class GoalsAPIsTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Account.objects.create_user(username='testuser', email='testuser@mail.com', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.goal = Goal.objects.create(
            title="My goal",
            description="My goal description",
            user=self.user.id, 
            finish_words="Test Finish Words"
        )

    def test_get_goals(self):
        response = self.client.get(reverse('goals_apis'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_goals_with_search(self):
        response = self.client.get(reverse('goals_apis'), {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_goal(self):
        data = {
            "title": "New Goal",
            "description": "New goal description",
            "missions": [
                {'content': 'Mission one'},
                {'content': 'Mission two'}
            ],
            "finish_words": "Congrates for finishing the goal"
        }
        response = self.client.post(reverse('goals_apis'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_goal_failure(self):
        data = {
            "title": "New Goal",
            "description": "",
            "missions": [
                {'content': 'Mission one'},
                {'content': 'Mission two'}
            ],
            "finish_words": "Congrates for finishing the goal"
        }
        response = self.client.post(reverse('goals_apis'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class GoalAPIsTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Account.objects.create_user(username='testuser', email='testuser@mail.com', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.goal = Goal.objects.create(
            title="My goal",
            description="My goal description",
            user=self.user.id, 
            finish_words="Test Finish Words"
        )

    def test_get_goal(self):
        response = self.client.get(reverse('goal_apis', kwargs={'pk': self.goal.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_goal_failure(self):
        response = self.client.get(reverse('goal_apis', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_goal(self):
        data = {'finish_words': 'Updated Finish Words'}
        response = self.client.patch(reverse('goal_apis', kwargs={'pk': self.goal.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_patch_goal_failure(self):
        data = {'finish_words': ''}
        response = self.client.patch(reverse('goal_apis', kwargs={'pk': self.goal.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_goal(self):
        response = self.client.delete(reverse('goal_apis', kwargs={'pk': self.goal.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_goal_failure(self):
        response = self.client.delete(reverse('goal_apis', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)