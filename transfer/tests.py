from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from .models import Transfer, Employee, DeliveryUnit

class ListTransferHistoryAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a delivery unit
        self.du = DeliveryUnit.objects.create(du_name='Test DU')

        # Create an employee
        self.employee = Employee.objects.create(name='Test Employee', du_id=self.du)

        # Create a user with a role (e.g., duhead)
        self.user = get_user_model().objects.create_user(
            username='duhead', password='testpassword', email='duhead@example.com',
            user_role=1, employee_id=self.employee
        )

        # Authenticate the client with the user's token
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    @patch('transfer.views.logger.error')
    def test_list_transfer_history_success(self, mock_logger_error):
        # Create sample transfer objects
        Transfer.objects.create(
            employee_id=self.employee,
            currentdu_id=self.du,
            targetdu_id=self.du,
            status=3,
            transfer_date='2024-02-17',
            initiated_by=self.employee
        )

        url = reverse('list-transfer-history')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('data' in response.data)
        self.assertEqual(len(response.data['data']), 4)  # Assuming one transfer is created
        # Add more assertions as needed based on your serializer output

    def test_list_transfer_history_unauthenticated(self):
        url = reverse('list-transfer-history')
        self.client.credentials()  # Clear authentication
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('transfer.views.logger.error')
    def test_list_transfer_history_exception(self, mock_logger_error):
        # Modify the user's employee to cause an exception
        self.user.employee_id = None
        self.user.save()

        url = reverse('list-transfer-history')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
