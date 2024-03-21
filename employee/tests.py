from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient,APITestCase
from rest_framework import status
from unittest.mock import patch
from .views import DuHeadAndDuList
from django.contrib.auth.models import User
from .models import Employee, DeliveryUnitMapping
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from employee.models import Employee
from delivery_unit.models import DeliveryUnit
from .serializers import *
from .models import Employee, DeliveryUnit  # Import your models
from user.models import User


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
 
 
# unit test case for PM listing API
class PMListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
 
        # Creating a DeliveryUnit instance
        self.du = DeliveryUnit.objects.create(du_name='DU1')
       
#        # Creating a test user with DU head role
        self.user = get_user_model().objects.create_user(
            username='Ravi', password='duhead', email="duhead@example.com",
            user_role=1 ,
            employee_id=Employee.objects.create(du_id=self.du)  # Associate the employee with the DU
 
        )
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
 
        # Creating a test PM user
        self.pm_user = get_user_model().objects.create_user(
            username='pm', password='pmpass', email="pm_email",
            user_role=2,  
            employee_id=Employee.objects.create(du_id=self.du, name='pm',mail_id="pm_email",)  
 
        )
 
     
    def test_pm_list_view(self):
        url = reverse('pm-list')  
        self.client.force_login(self.user)  
 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'PM listing successful')
        self.assertTrue('data' in response.data)
        self.assertEqual(len(response.data['data']), 1)
 
 
    def test_pm_list_view_no_pm_available(self):
        # Delete the PM user created in setUp() to simulate no PMs available
        self.pm_user.delete()
        url = reverse('pm-list')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No Project Managers available ')
 

# unit test case for BandListing API
class BandListViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
       
        # Creating a test user with DU head role
        self.user = get_user_model().objects.create_user(
            username='duhead', password='duhead', email="duhead@example.com",
            user_role=1  
        )
        self.token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
 
    def test_get_band_levels(self):
        url = reverse('band-list')
 
        # Assuming a DU head user is authenticated
        self.client.force_login(self.user)  
       
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Band levels retrieved successfully')
 
        # Assuming there are 5 band levels
        self.assertEqual(len(response.data['band_levels']), 5)
        self.assertListEqual(response.data['band_levels'], ["A1", "A2", "B1", "B2", "C1"])
 
    def test_post_not_allowed(self):
        url = reverse('band-list')  
        self.client.force_login(self.user)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['message'], 'Method "POST" not allowed.')
 
 
# unit test case for employeeListing API
class EmployeeListCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test admin user
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', user_role=5)
        self.token = AccessToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.client.force_login(self.admin_user)  
       
        # Create some test employees
        Employee.objects.create(employee_number='001', name='Employee 1', mail_id='employee1@example.com', designation='Developer')
        Employee.objects.create(employee_number='002', name='Employee 2', mail_id='employee2@example.com', designation='Designer')
        Employee.objects.create(employee_number='003', name='Employee 3', mail_id='employee3@example.com', designation='Manager')
 
    def test_list_employees(self):
        response = self.client.get('/api/v1/employee/employee-list/')  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # Assuming that there are 3 test employees
        self.assertEqual(response.data['results'][0]['name'], 'Employee 1')  # Assume that first employee's name is 'Employee 1'
