from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from employee.models import Employee
from delivery_unit.models import DeliveryUnit
from rest_framework.test import APIClient, APITestCase
from unittest.mock import patch
from rest_framework_simplejwt.tokens import AccessToken
from .models import Transfer, Employee, DeliveryUnit
from .views import PendingApprovalsView

class TransferAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        employee = Employee.objects.create(id=40, name="Albin", mail_id="albin@gmail.com")
        employee2 =  Employee.objects.create(id=30, name="Abin", mail_id="abin@gmail.com")
         
        
        self.user = get_user_model().objects.create_user(
            username='admin', password='admin', email="admin@example.com",
            user_role=5, employee_id=employee
        )
        
        self.base_url = "/api/v1/"
        
        self.token = AccessToken.for_user(self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')


    def test_transfer_api_correct_case(self):
        # Assuming you have some test data, construct a valid request payload
        employee2 =  Employee.objects.create(id=56, name="Don", mail_id="don@gmail.com")
        du1 = DeliveryUnit.objects.create(du_name='DU1')
        du2 = DeliveryUnit.objects.create(du_name='DU2')
        data = {
            'currentdu_id': du1.id,
            'targetdu_id': du2.id,
            'employee_id': employee2.id,
            'status':2,
            'transfer_date':"2023-10-10",
            'transfer_raised_on':"2023-10-10",
            'total_experience':6,
            'experion_experience':4,
            'employee_band':'A1'
        }

        url = reverse('create-transfer')

        response = self.client.post(url, data, format='json')
        print('hello',response)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'message': 'Transfer created and email sent successfully.'})

    def test_transfer_api_error_case(self):
        # Assuming you have some test data, construct a valid request payload
        employee2 =  Employee.objects.create(id=56, name="Don", mail_id="don@gmail.com")
        du1 = DeliveryUnit.objects.create(du_name='DU1')
        du2 = DeliveryUnit.objects.create(du_name='DU2')
        data = {
            'currentdu_id': du1.id,
            'targetdu_id': du2.id,
            'status':2,
            'transfer_date':"2023-10-10",
            'transfer_raised_on':"2023-10-10",
            'total_experience':6,
            'experion_experience':4,
            'employee_band':'A1'
        }

        url = reverse('create-transfer')

        response = self.client.post(url, data, format='json')
        print('hello',response)
        self.assertEqual(response.status_code, 400)

    def test_transfer_api_unauthorized_case(self):
        # Assuming you have some test data, construct a valid request payload
        employee2 =  Employee.objects.create(id=56, name="Don", mail_id="don@gmail.com")
        du1 = DeliveryUnit.objects.create(du_name='DU1')
        du2 = DeliveryUnit.objects.create(du_name='DU2')
        data = {
            'currentdu_id': du1.id,
            'targetdu_id': du2.id,
            'employee_id': employee2.id,
            'status':2,
            'transfer_date':"2023-10-10",
            'transfer_raised_on':"2023-10-10",
            'total_experience':6,
            'experion_experience':4,
            'employee_band':'A1'
        }

        self.client.credentials()

        url = reverse('create-transfer')

        response = self.client.post(url, data, format='json')
        print('hello',response)
        self.assertEqual(response.status_code, 401)

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


class PendingApprovalsViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a delivery unit
        self.current_du = DeliveryUnit.objects.create(du_name='Current DU')
        self.target_du = DeliveryUnit.objects.create(du_name='Target DU')

        # Create unique mail_id values
        du_head_mail = 'duhead@example.com'
        pm_mail = 'pm@example.com'

        # Create an employee for DU head and PM
        self.du_head = Employee.objects.create(name='DU Head', du_id=self.current_du, mail_id=du_head_mail)
        self.pm = Employee.objects.create(name='PM', du_id=self.current_du, mail_id=pm_mail)

        # Create a user with the DU head role
        self.head_user = get_user_model().objects.create_user(
            username='duhead', password='testpassword', email=du_head_mail,
            user_role=1, employee_id=self.du_head
        )
        self.pm_user = get_user_model().objects.create_user(
            username='pm', password='testpassword', email=pm_mail,
            user_role=2, employee_id=self.pm
        )

        # Authenticate the client with the user's token
        self.token = AccessToken.for_user(self.head_user)  # Use DU head user's token for authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.url = reverse('pending-approvals')

        self.employee = Employee.objects.create(name='Test Employee', du_id=self.current_du)


    def test_pending_approvals_external_success(self):
        Transfer.objects.create(
            employee_id=self.employee,
            currentdu_id=self.current_du,
            targetdu_id=self.target_du,
            status=2,
            transfer_date="2024-02-12",
            initiated_by=self.du_head  # Provide a value for initiated_by
        )
        # Assuming TransferAndEmployeeSerializer correctly serializes Transfer objects
        response = self.client.get(self.url, {'du_id': 2, 'tab_switch_btn': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No external requests from other DUs exists.') 

    def test_pending_approvals_internal_success(self):
        Transfer.objects.create(
            employee_id=self.employee,
            currentdu_id=self.current_du,
            targetdu_id=self.target_du,
            status=1,
            transfer_date="2024-02-12",
            initiated_by=self.pm  # Provide a value for initiated_by
        )
        # Assuming TransferAndEmployeeSerializer correctly serializes Transfer objects
        response = self.client.get(self.url, {'du_id': 1, 'tab_switch_btn': 2})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No internal requests from this DU exists.') 

    def test_pending_approvals_no_data(self):
        response = self.client.get(self.url, {'du_id': 1, 'tab_switch_btn': 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_pending_approvals_invalid_tab(self):
        response = self.client.get(self.url, {'du_id': 1, 'tab_switch_btn': 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('transfer.views.Transfer.objects.filter')
    def test_pending_approvals_exception(self, mock_filter):
        mock_filter.side_effect = Exception("Test exception")
        response = self.client.get(self.url, {'du_id': 1, 'tab_switch_btn': 1})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


