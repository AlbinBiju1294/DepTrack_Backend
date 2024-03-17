from rest_framework.test import APITestCase
import logging
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from employee.models import Employee
from delivery_unit.models import DeliveryUnit

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

