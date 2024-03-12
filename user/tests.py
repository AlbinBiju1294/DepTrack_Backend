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
        employee2 =  Employee.objects.create(id=30, name="Abin", mail_id="abin@gmail.com")
         
        
        self.user = get_user_model().objects.create_user(
            username='admin', password='admin', email="admin@example.com",
            user_role=5, employee_id=employee
        )

        self.regular_user = get_user_model().objects.create_user(
            username='regularuser', password='regular', email="regular@example.com",
            user_role=4, employee_id=employee2
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
        self.assertEqual(get_user_model().objects.count(), 3)
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
        self.assertEqual(get_user_model().objects.count(), 2)

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
        self.assertEqual(get_user_model().objects.count(), 2)

    #Test User list

    def test_list_users_as_admin(self):
        """Test that an admin user can retrieve the list of users"""
        self.client.force_authenticate(user=self.user)
        url = reverse('userslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        print(response.data)

    def test_list_users_as_regular_user(self):
        """Test that a regular user cannot retrieve the list of users"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('userslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print(response)

    def test_list_users_no_auth(self):
        """Test that an unauthenticated user cannot retrieve the list of users"""
        self.client.credentials(HTTP_AUTHORIZATION='')
        url = reverse('userslist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print(response)