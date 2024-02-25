
import logging
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient,APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken


user = get_user_model()

logger = logging.getLogger("django")

class UserAuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        url = reverse('registration')
        data = {'username': 'testuser', 'password': 'testpass', 'email': 'test@example.com',"user_role":2,"employee_id":38348}
        response = self.client.post(url, data, format='json')
        # logger.info(f"USER_TEST |  Registration API Response : {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')
