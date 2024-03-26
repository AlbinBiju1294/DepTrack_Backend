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
from datetime import datetime, timedelta

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
        self.assertEqual(Transfer.objects.count(),1)

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
        self.assertEqual(response.status_code, 401)

class ListInitiatedTransfersAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a delivery unit
        self.du = DeliveryUnit.objects.create(du_name='Test DU')
        self.du1 = DeliveryUnit.objects.create(du_name='Test DU new')

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
    def test_list_initiated_requests_success(self, mock_logger_error):
        # Create sample transfer objects
        transfer = Transfer.objects.create(
        employee_id=self.employee,
        currentdu_id=self.du,
        targetdu_id=self.du1,
        status=2,  
        transfer_date="2024-02-02",  
        initiated_by=self.employee, 
        )

        print(transfer)

        url = reverse('track-initiated-request')
        response = self.client.get(url,{'du_id':self.du.id})
        print('hello track',response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('data' in response.data)  

    def test_list_initiated_requests_unauthenticated(self):
        url = reverse('track-initiated-request')
        self.client.credentials()  # Clear authentication
        response = self.client.get(url,{'du_id':self.du.id})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('transfer.views.logger.error')
    def test_list_initiated_requests_exception(self, mock_logger_error):
        # Modify the user's employee to cause an exception
        self.user.employee_id = None
        self.user.save()

        url = reverse('track-initiated-request')
        response = self.client.get(url,{'du_id':self.du.id})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
        self.assertEqual(len(response.data['data']), 4) 

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




from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from datetime import datetime, timedelta
from .models import DeliveryUnit, Employee, Transfer
from .views import NoOfTransfersInDUsAPIView

class NoOfTransfersInDUsAPIViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create sample DeliveryUnit objects
        cls.du1 = DeliveryUnit.objects.create(du_name='DU 1')
        cls.du2 = DeliveryUnit.objects.create(du_name='DU 2')

        # Create Employee instances
        cls.employee1 = Employee.objects.create(
            employee_number='EMP001',
            name='John Doe',
            mail_id='john@example.com',
            designation='Developer',
            du_id=cls.du1
        )

        cls.employee2 = Employee.objects.create(
            employee_number='EMP002',
            name='Jane Smith',
            mail_id='jane@example.com',
            designation='Designer',
            du_id=cls.du2
        )

        cls.employee3 = Employee.objects.create(
            employee_number='EMP003',
            name='Alice Johnson',
            mail_id='alice@example.com',
            designation='Manager',
            du_id=cls.du1
        )
        cls.employee4 = Employee.objects.create(
            employee_number='EMP001',
            name='John',
            mail_id='johnd@example.com',
            designation='Developer',
            du_id=cls.du2
        )

        # Create sample Transfer objects
        thirty_days_ago = datetime.now() - timedelta(days=30)
        Transfer.objects.create(employee_id=cls.employee1, currentdu_id=cls.du1, targetdu_id=cls.du2, status=3,
                                transfer_date=thirty_days_ago, newpm_id=cls.employee2, initiated_by=cls.employee3)
        Transfer.objects.create(employee_id=cls.employee4, currentdu_id=cls.du2, targetdu_id=cls.du1, status=3,
                                transfer_date=thirty_days_ago, newpm_id=cls.employee3, initiated_by=cls.employee2)

    def setUp(self):
        # Create a user
        self.user = get_user_model().objects.create_user(
            username='duhead', password='testpassword', email='duhead@example.com',
            user_role=1, employee_id=self.employee1
        )

        # Create an access token for the user
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_number_of_transfers_in_dus(self):
        # Create a GET request
        url = reverse('bargraph-data')
        response = self.client.get(url)

        # Check response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response data
        self.assertIn('data', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(len(response.data['data']), 2)  
    
    def test_get_number_of_transfers_in_dus_unauthenticated(self):
        # Clear authentication
        self.client.credentials()

        # Create a GET request without authentication
        url = reverse('bargraph-data')
        response = self.client.get(url)

        # Check response status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
