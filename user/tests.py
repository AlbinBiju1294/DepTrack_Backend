import logging
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient,APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import User
from employee.models import Employee


user = get_user_model()

logger = logging.getLogger("django")

class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        employee = Employee.objects.create(id=40, name="Albin", mail_id="albin@gmail.com")
        
        self.user = get_user_model().objects.create_user(
            username='admin', password='admin', email="admin@example.com",
            user_role=5, employee_id=employee
        )
        
        self.base_url = "/api/v1/"
        
        self.token = AccessToken.for_user(self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_user_registration(self):
        url = reverse('registration')
        employee1 = Employee.objects.create(id=45, name="jdfnjk", mail_id="ajsn@gmail.com")
        data = {
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test1@example.com',
            "user_role": 2, 
            "employee_id": employee1.id 
        }
        

        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 2)
        self.assertEqual(get_user_model().objects.last().username, 'testuser')

    def test_user_registration_unauthorized(self):
        url = reverse('registration')
        self.token = None
        employee1 = Employee.objects.create(id=45, name="jdfnjk", mail_id="ajsn@gmail.com")
        data = {
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test1@example.com',
            "user_role": 2, 
            "employee_id": employee1.id 
        }

        self.client.credentials()
        
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_user_registration_fail(self):
        url = reverse('registration')
        self.token = None
        employee1 = Employee.objects.create(id=45, name="jdfnjk", mail_id="ajsn@gmail.com")
        data = {
            'password': 'testpass',
            'email': 'test1@example.com',
            "user_role": 2, 
            "employee_id": employee1.id 
        }
        
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_user_model().objects.count(), 1)
