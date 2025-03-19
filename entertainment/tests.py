from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Entertainment, TYPE_CHOICES, STATUS_CHOICES
from .serializers import EntertainmentSerializer
from authentication.models import Account

class EntertainmentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Account.objects.create_user(username='testuser', email='testuser@mail.com', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.entertainment_data = {
            'title': 'Example Season 2',
            'description': 'Example Season 2 continues after Example Season 1',
            'image': 'https://media.istockphoto.com/id/1316134499/photo/a-concept-image-of-a-magnifying-glass-on-blue-background-with-a-word-example-zoom-inside-the.jpg?s=612x612&w=0&k=20&c=sZM5HlZvHFYnzjrhaStRpex43URlxg6wwJXff3BE9VA=',
            'link': 'http://example.com',
            'type': TYPE_CHOICES[0][0],
            'status': STATUS_CHOICES[0][0],
            'user': self.user.id
        }
        self.entertainment = Entertainment.objects.create(**self.entertainment_data)

    def test_add_material_by_link_success(self):
        response = self.client.post(reverse('add_material_by_link'), {
            'link': 'http://myanimelist.net/anime/1',
            'status': 'current'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_material_by_link_invalid_link(self):
        response = self.client.post(reverse('add_material_by_link'), {
            'link': 'http://invalidlink.com',
            'status': 'current'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_material_manually_success(self):
        response = self.client.post(reverse('add_material_manually'), self.entertainment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_material_manually_invalid_data(self):
        invalid_data = self.entertainment_data.copy()
        invalid_data['type'] = 'invalid_type'
        response = self.client.post(reverse('add_material_manually'), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_materials_success(self):
        response = self.client.get(reverse('get_all_materials'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_special_materials_success(self):
        response = self.client.get(reverse('get_special_materials'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_material_operations_get_success(self):
        response = self.client.get(reverse('material_operations', kwargs={'pk': self.entertainment.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_material_operations_patch_success(self):
        response = self.client.patch(reverse('material_operations', kwargs={'pk': self.entertainment.id}), {'status': 'done'})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_material_operations_delete_success(self):
        response = self.client.delete(reverse('material_operations', kwargs={'pk': self.entertainment.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_materials_success(self):
        response = self.client.get(reverse('search_materials'), {'type': TYPE_CHOICES[0][0]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)