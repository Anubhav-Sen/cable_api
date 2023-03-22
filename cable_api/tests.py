from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class TestUsers(APITestCase):
    """
    A class to test the "api/users/" endpoint.
    """
    def setUp(self):
        pass
    
    def test_users_GET(self):
        """
        A method to test the GET method of the "api/users/" endpoint.
        """
        endpoint = reverse('users')

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)