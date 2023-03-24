from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from cable_api.factory import UserFactory

class TestUsers(APITestCase):
    """
    A class to test the "api/users/" endpoint.
    """
    def setUp(self):
        
        self.user_factory = UserFactory.create_batch(5)
    
    def test_users_GET(self):
        """
        A method to test the GET method of the "api/users/" endpoint.
        """
        endpoint = reverse('users')

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 5)