from django.test import TestCase
from .models import User
from employee.models import employee
from rest_framework.test import APIClient,APITestCase
from django.contrib.auth import get_user_model
import logging
from rest_framework import status

from django.test import TestCase
from django.urls import reverse
from .models import*
from rest_framework_simplejwt.tokens import AccessToken


# Create your tests here.
user = get_user_model()

logger = logging.getLogger("django")

class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Du1 = DeliveryUnit.objects.create( du_name="jdfnjk")
        
        self.user = get_user_model().objects.create_user(
            username='admin', password='admin', email="admin@example.com",
            user_role=5, employee_id=employee

        )
        self.base_url = "/api/v1/delivery_unit/"
        
        self.token = AccessToken.for_user(self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_Du_creation(self):
        url = reverse('create-deliveryunit')
        Du1 = DeliveryUnit.objects.create( du_name="jdfnjk")
        data = {
            'du_name': 'DU1',
        
        }
        response = self.client.post(url, data, format='json')
        print(response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryUnit.objects.count(), 1)
        self.assertEqual(DeliveryUnit.objects.last().du_name, 'DU1')