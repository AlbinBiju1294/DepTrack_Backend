from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from .views import DuHeadAndDuList
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
from .serializers import *


user = get_user_model()

class PotentialDuHeadsTestCase(TestCase):
    def setUp(self):

        self.base_url = "/api/v1/"
        self.client = APIClient()
        self.employee = Employee.objects.create(id=40, name="Albin", mail_id="albin@gmail.com")
        self.employee2 =  Employee.objects.create(id=30, name="Abin", mail_id="abin@gmail.com")
        self.employee3 =  Employee.objects.create(id=20, name="Absfsdin", mail_id="sdfabin@gmail.com")

        self.employee4 =  Employee.objects.create(id=33, name="Aden", mail_id="abesn@gmail.com")
        self.user = get_user_model().objects.create_user(
            username='user1', password='user1', email="admiddafn@example.com",
            user_role=1, employee_id=self.employee
        )
        self.admin = get_user_model().objects.create_user(
            username='admin', password='usddder1', email="admin@example.com",
            user_role=5, 
        )
        self.user2 = get_user_model().objects.create_user(
            username='user2', password='user2', email="admfsdin@example.com",
            user_role=1, employee_id=self.employee2
        )
        self.user4 = get_user_model().objects.create_user(
            username='user4', password='userd2', email="admfddsdin@example.com",
            user_role=4, employee_id=self.employee4
        )

       
        
        self.token = AccessToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        
        # Create test delivery unit mapping
        self.mapping = DeliveryUnitMapping.objects.create(du_head_id=self.employee2,hrbp_id=self.employee3)
        
        
    def test_get_potential_du_heads(self):
        url = reverse('get-du-candidates')
        response = self.client.get(url)  
        # Check if response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        expected_data = {
            "data": [
                {"employee_id": self.employee.id, "name": self.employee.name},
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
                {"employee_id": self.employee4.id, "name": self.employee4.name},
            ],
            "message": "hrbp Candidates Listed"
        }
        self.assertEqual(response.data, expected_data)

class DuHeadAndDuListTestCase(TestCase):
    def setUp(self):
        self.base_url = "/api/v1/"
        self.client = APIClient()
        self.employee2 =  Employee.objects.create(id=30, name="Abin", mail_id="abin@gmail.com")
        self.employee3 =  Employee.objects.create(id=20, name="Absfsdin", mail_id="sdfabin@gmail.com")
        self.du1=DeliveryUnit.objects.create(id=1,du_name="DU3")
        self.du2=DeliveryUnit.objects.create(id=2,du_name="DU2")
        self.mapping1 = DeliveryUnitMapping.objects.create(du_head_id=self.employee2, du_id=self.du1)
        self.mapping2 = DeliveryUnitMapping.objects.create(du_head_id=self.employee3, du_id=self.du2)
        self.admin = get_user_model().objects.create_user(
            username='admin', password='usddder1', email="admin@example.com",
            user_role=5, 
        )
        self.token = AccessToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    def test_list_du_heads_and_dus_success(self):
        url = reverse('duheadlist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("data" in response.data)
        self.assertTrue("message" in response.data)
        self.assertEqual(response.data["message"], "DU heads Listed Successfully")
        serializer = DuAndEmployeeSerializer(instance=[self.mapping1, self.mapping2], many=True)
        self.assertEqual(response.data["data"], serializer.data)

    def test_list_no_du_heads(self):
        # Delete all existing DeliveryUnitMapping objects
        DeliveryUnitMapping.objects.all().delete()
        url = reverse('duheadlist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue("data" in response.data)
        self.assertTrue("error" in response.data)
        self.assertEqual(response.data["error"], "No DU heads")
        self.assertEqual(response.data["data"], [])

    def test_internal_server_error(self):
        # Simulate internal server error by removing serializer_class
        with patch.object(DuHeadAndDuList, 'get_serializer_class', return_value=None):
            url = reverse('duheadlist')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertTrue("error" in response.data)