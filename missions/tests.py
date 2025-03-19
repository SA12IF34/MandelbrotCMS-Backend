from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import List, Mission
from authentication.models import Account

class ListAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Account.objects.create_user(email='test@example.com', password='password123', username='testuser')
        self.client.force_authenticate(user=self.user)
        self.list = List.objects.create(title='Test List', date='2025-01-21', user=self.user.id)
        self.mission = Mission.objects.create(content='Test Mission', list=self.list)

    def test_get_all_lists_success(self):
        response = self.client.get(reverse('lists_apis'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_lists_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('lists_apis'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_list_success(self):
        data = {
            'list': {
                'title': 'New List',
                'date': '2025-01-20'
            },
            'missions': [
                {
                    'content': 'Mission content.'
                }
            ]
        }
        response = self.client.post(reverse('lists_apis'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_list_failure(self):
        data = {
            'list': {
                'title': '',
                'date': '2023-10-11'
            },
            'missions': []
        }
        response = self.client.post(reverse('lists_apis'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_today_list_success(self):
        response = self.client.get(reverse('get_today_list', kwargs={'date': '2025-1-21'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_today_list_not_found(self):
        response = self.client.get(reverse('get_today_list', kwargs={'date': '2023-10-11'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_list_success(self):
        response = self.client.get(reverse('list_apis', kwargs={'pk': self.list.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list_not_found(self):
        response = self.client.get(reverse('list_apis', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_list_success(self):
        data = {'title': 'Updated List'}
        response = self.client.patch(reverse('list_apis', kwargs={'pk': self.list.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_list_failure(self):
        data = {'title': ''}
        response = self.client.patch(reverse('list_apis', kwargs={'pk': self.list.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_list_success(self):
        response = self.client.delete(reverse('list_apis', kwargs={'pk': self.list.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_list_not_found(self):
        response = self.client.delete(reverse('list_apis', kwargs={'pk': 348}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mission_operations_success(self):
        data = {'content': 'Updated Mission'}
        response = self.client.patch(reverse('mission_operations', kwargs={'pk': self.mission.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_mission_operations_failure(self):
        data = {'content': ''}
        response = self.client.patch(reverse('mission_operations', kwargs={'pk': self.mission.id}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_sequence_list_failure(self):
        response = self.client.get(reverse('get_sequence_list', kwargs={'pk': self.list.id,'sequence': 'next'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
