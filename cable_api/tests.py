import json
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
        self.maxDiff = None
    
    def test_users_GET(self):
        """
        A method to test the GET method of the "api/users/" endpoint.
        """
        endpoint = reverse('users')

        response = self.client.get(endpoint)

        users_list = []

        for user in self.user_factory:

            user_dict = {
                'id': user.id,
                'user_name': user.user_name,
                'email_address': user.email_address,
                'profile_image': user.profile_image.url
            }

            users_list.append(user_dict)

        expected_response = {'users': users_list}

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
        