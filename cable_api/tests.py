import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from cable_api.factory import UserFactory

class TestUsers(APITestCase):
    """
    A class to test the "api/users/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory    
        self.user_factory.create_batch(5)
        self.maxDiff = None

    def test_users_GET(self):
        """
        A method to test the GET method of the "api/users/" endpoint.
        """
        endpoint = reverse('users')

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

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_users_POST(self):
        """
        A method to test the POST method of the "api/users/" endpoint.
        """
        endpoint = reverse('users')

        request_dict = {
            
        }

        users = get_user_model().objects.all()
        print(users)

        response = self.client.post(endpoint)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

    def tearDown(self):
        """
        A method to teardown the data generated using the setup method.
        """
        self.user_factory.reset_sequence()