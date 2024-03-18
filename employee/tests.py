from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Employee, DeliveryUnitMapping
from .views import PotentialDuHeads
import logging
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from employee.models import Employee
from delivery_unit.models import DeliveryUnit


user = get_user_model()

class PotentialDuHeadsTestCase(TestCase):
    def setUp(self):

        self.base_url = "/api/v1/"
        self.client = APIClient()
        self.employee = Employee.objects.create(id=40, name="Albin", mail_id="albin@gmail.com")
        self.employee2 =  Employee.objects.create(id=30, name="Abin", mail_id="abin@gmail.com")
        self.employee3 =  Employee.objects.create(id=330, name="Aden", mail_id="abesn@gmail.com")
        self.user = get_user_model().objects.create_user(
            username='user1', password='user1', email="admiddafn@example.com",
            user_role=1, employee_id=self.employee
        )
        self.admin = get_user_model().objects.create_user(
            username='admin', password='usddder1', email="admin@example.com",
            user_role=5, 
        )
        self.user = get_user_model().objects.create_user(
            username='user2', password='user2', email="admfsdin@example.com",
            user_role=1, employee_id=self.employee2
        )
        self.user3 = get_user_model().objects.create_user(
            username='user3', password='userd2', email="admfddsdin@example.com",
            user_role=4, employee_id=self.employee3
        )

       
        
        self.token = AccessToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        
        # Create test delivery unit mapping
        self.mapping = DeliveryUnitMapping.objects.create(du_head_id=self.employee2)
        
    def test_get_potential_du_heads(self):
        url = reverse('get-du-candidates')
        response = self.client.get(url)  
        # Check if response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_data = {
            "data": [
                {"employee_id": self.employee2.id, "name": self.employee2.name},
            ],
            "message": "du Head candidates listed"
        }
        self.assertEqual(response.data, expected_data)
        
    def test_get_potential_hrbps(self):
        url = reverse('get-hrbp-candidates')
        response = self.client.get(url)  
        # Check if response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_data = {
            "data": [
                {"employee_id": self.employee3.id, "name": self.employee3.name},
            ],
            "message": "du Head candidates listed"
        }
        self.assertEqual(response.data, expected_data)