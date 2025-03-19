from django.test import TestCase
from .serializers import ProjectSerializer, PartitionSerializer
from rest_framework.test import APIClient
from .models import Project, Partition
import datetime

class ProjectsSuccessTestCase(TestCase): # For 200s responses

    base_url = '/sessions_manager/apis/'
    
    def setUp(self):
        self.client = APIClient()

        data = {
            "email": "user@mail.com",
            "username": "user",
            "password": "user123"
        }

        self.client.post('/authentication/signup/', data=data)

    
    def test_create_project(self):
        res = self.client.post(self.base_url+'projects/', data={
           "project": {
                "title": "Project 1",
                "description": "Project 1 description"
           }, "partitions": [
               {
                   "title": "part 1",
                   "description": "part 1 description",
                   "start_date": datetime.date.today()
               }, {
                   "title": "part 2"
               }
           ]
        }, format='json')

        status_code = res.status_code

        self.assertEqual(status_code, 201)
    
    def test_get_all_projects(self):
        self.test_create_project()

        res = self.client.get(self.base_url+'projects/')
        status_code = res.status_code
        json = res.json()

        self.assertEqual(status_code, 200)
        self.assertEqual(type(json), list)
        self.assertEqual(len(json), 1)

    
    def test_get_project(self):
        self.test_create_project()

        res = self.client.get(self.base_url+'projects/1/')
        status_code = res.status_code
        json = res.json()

        self.assertEqual(status_code, 200)
        self.assertEqual(type(json), dict)
        self.assertEqual(json['title'], 'Project 1')
        self.assertEqual(len(json['partitions']), 2)

        return json
    
    def test_edit_project(self):
        self.test_create_project()

        res = self.client.patch(self.base_url+'projects/1/', data={
            'finish_date': datetime.date.today()
        }, format='json')

        status_code = res.status_code

        self.assertEqual(status_code, 202)
    
    def test_update_partition_and_start_project(self):
        self.test_create_project()

        res = self.client.patch(self.base_url+'partitions/1/', format='json')
        status_code = res.status_code

        self.assertEqual(status_code, 202) 
        # Updating first partition to done in test case ends up with 202
        # It works, trust me bro :)
    
    def test_delete_partition(self):
        self.test_create_project()

        res = self.client.delete(self.base_url+'partitions/2/')
        status_code = res.status_code

        self.assertEqual(status_code, 202)

    def test_delete_project(self):
        self.test_create_project()

        res = self.client.delete(self.base_url+'projects/1/')
        status_code = res.status_code

        self.assertEqual(status_code, 204)

    def test_delete_project_by_partitions(self):
        self.test_create_project()

        res1 = self.client.delete(self.base_url+'partitions/1/', format='json')
        res2 = self.client.delete(self.base_url+'partitions/2/', format='json')

        self.assertEqual(res1.status_code, 202)
        self.assertEqual(res2.status_code, 204)


class ProjectsFailureTestCase(TestCase): # For 400s responses

    base_url = '/sessions_manager/apis/'

    def setUp(self):
        self.client = APIClient()

        data = {
            "email": "user@mail.com",
            "username": "user",
            "password": "user123"
        }

        self.client.post('/authentication/signup/', data=data)

        self.client.post(self.base_url+'projects/', data={
           "project": {
                "title": "Project 1",
                "description": "Project 1 description"
           }, "partitions": [
               {
                   "title": "part 1",
                   "description": "part 1 description",
                   "start_date": datetime.date.today()
               }, {
                   "title": "part 2"
               }
           ]
        }, format='json')

    def test_create_project_1(self):

        res = self.client.post(self.base_url+'projects/', data={
            'project': {
                'title': 'Project 2'
            },
            'partitions': [
                {
                   "title": "part 3",
                   "description": "part 3 description",
                }, {
                   "title": "part 4"
                }
            ]
        }, format='json')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['error'], 'project')

    def test_create_project_2(self):
        res = self.client.post(self.base_url+'projects/', data={
            'project': {
                'title': 'Project 2',
                'description': 'Project 2 description'
            },
            'partitions': []
        }, format='json')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['error'], 'partition')

    def test_create_project_3(self):
        res = self.client.post(self.base_url+'projects/', data={
            'project': {
                'title': 'Project 2',
                'description': 'Project 2 description'
            },
            'partitions': [
                {
                   "title": "part 3",
                   "description": "part 3 description",
                   "start_date": datetime.date.today()
                }, {
                   "description": "partition 4 description"
                }
            ]
        }, format='json')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['error'], 'partition')

    def test_get_project(self): 
        # If this test passes,
        # then all one-project base apis are considered passed since they all work the same way

        res = self.client.get(self.base_url+'projects/222/')

        self.assertEqual(res.status_code, 404)

    def test_update_partition(self):

        res = self.client.patch(self.base_url+'partitions/1/', data={'done': 'hello'}, format='json')

        self.assertEqual(res.status_code, 400)

    
