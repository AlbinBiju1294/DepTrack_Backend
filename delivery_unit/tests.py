from django.test import TestCase
from employee.models import Employee
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
import logging
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from .models import*
from rest_framework_simplejwt.tokens import AccessToken
from unittest.mock import patch
from employee.models import DeliveryUnit, Employee
from rest_framework_simplejwt.tokens import AccessToken

class DashboardDuDetailsTestCase(TestCase):
    #Here the accessing user is a du head, we can change it to admin, pm or hrbp in the setUp function
    def setUp(self):
        self.client = APIClient()

        # Create a delivery unit and employee
        self.du = DeliveryUnit.objects.create(du_name='Test DU')
        self.employee = Employee.objects.create(name='Test Employee', du_id=self.du)

        # Create a user with duhead role
        self.user = get_user_model().objects.create_user(
            username='duhead', password='testpassword', email='duhead@example.com',
            user_role=1, employee_id=self.employee
        )

        # Authenticate the client with the user's token
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    @patch('delivery_unit.views.logger.error')                              # Mock logger.error to prevent actual logging
    def test_get_dashboard_details(self, mock_logger_error):
        url = reverse('dashboard-du-details')
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('data', response.data)
        self.assertIn('du_name', response.data['data'])
        self.assertIn('no_of_pms', response.data['data'])
        self.assertIn('no_of_employees', response.data['data'])

    def test_get_dashboard_details_unauthenticated(self):
        url = reverse('dashboard-du-details')
        self.client.credentials()                                                   # Clear authentication
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_dashboard_details_exception(self):
        # Modify the user's employee to cause an exception
        self.user.employee_id = None
        self.user.save()

        url = reverse('dashboard-du-details')
        
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
user = get_user_model()

logger = logging.getLogger("django")