from django.test import TestCase
from rest_framework.test import APIClient
from .models import Course, Section
from .serializers import CourseSerializer, SectionSerializer

class CoursesSuccessTestCase(TestCase):

    base_url = '/learning_tracker/apis/'

    def setUp(self):
        self.client = APIClient()

        data = {
            "email": "user@mail.com",
            "username": "user",
            "password": "user123"
        }

        self.client.post('/authentication/signup/', data=data)


    def test_add_course_youtube(self):
        data = {
            'link': 'https://youtu.be/sdc9QK735to?si=AcOkzkqVrdC7vD69',
            'status': 'current'
        }

        res = self.client.post(self.base_url+'courses/', data=data, format='json')

        self.assertEqual(res.status_code, 201)

    
    def test_add_course_coursera(self):
        data = {
            'link': 'https://www.coursera.org/professional-certificates/microsoft-project-management?trk_ref=camodule',
            'status': 'current'
        }

        res = self.client.post(self.base_url+'courses/', data=data, format='json')

        self.assertEqual(res.status_code, 201)

    
    def test_get_all_courses(self):
        self.test_add_course_youtube()
        self.test_add_course_coursera()

        res = self.client.get(self.base_url+'courses/', format='json')
        json = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(json['current']), 2)

    
    def test_get_course(self):
        self.test_add_course_youtube()
        self.test_add_course_coursera()

        res = self.client.get(self.base_url+'courses/2/', format='json')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['id'], 2)

    
    def test_update_section(self):
        self.test_add_course_coursera()

        res = self.client.patch(self.base_url+'update-section/1/', data={'done': True}, format='json')

        self.assertEqual(res.status_code, 202)

    
    def test_update_course(self):
        self.test_add_course_youtube()
        
        res = self.client.patch(self.base_url+'courses/1/', data={'status': 'done'}, format='json')

        self.assertEqual(res.status_code, 202)
        

    def test_delete_course(self):
        self.test_add_course_coursera()

        res = self.client.delete(self.base_url+'courses/1/')

        self.assertEqual(res.status_code, 204)



class CoursesFailureTestCase(TestCase):

    base_url = '/learning_tracker/apis/'

    def setUp(self):
        self.client = APIClient()

        data = {
            "email": "user@mail.com",
            "username": "user",
            "password": "user123"
        }

        self.client.post('/authentication/signup/', data=data)

        self.client.post(self.base_url+'courses/', data={
            'link': 'https://youtu.be/sdc9QK735to?si=AcOkzkqVrdC7vD69',
            'status': 'current'
        }, format='json')

        self.client.post(self.base_url+'courses/', data={
            'link': 'https://www.coursera.org/professional-certificates/microsoft-project-management?trk_ref=camodule',
            'status': 'done'
        }, format='json')


    def test_create_course_fail_0(self):
        data = {
            'link': 'https://www.coursera.org/professional-certificates/microsoft-project-management?trk_ref=camodule',
            'status': ''
        }
        
        res = self.client.post(self.base_url+'courses/', data=data, format='json')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['data'], 0)


    def test_create_course_fail_1(self):
        data = {
            'link': 'https://saifchan.online/my-course/',
            'status': 'done'
        }

        res = self.client.post(self.base_url+'courses/', data=data, format='json')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['data'], 1)

    def test_create_course_fail_2(self):
        data = {
            'link': 'https://www.coursera.org/professional-certificates/microsoft-project-management?trk_ref=camodule'
        }

        res = self.client.post(self.base_url+'courses/', data=data, format='json')

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()['data'], 2)

    def test_get_course_fail(self):

        res = self.client.get(self.base_url+'courses/33/', format='json')

        self.assertEqual(res.status_code, 404)

    def test_update_section_fail(self):
        
        res = self.client.patch(self.base_url+'update-section/1/', data={'done': True}, format='json')

        self.assertEqual(res.status_code, 406)


