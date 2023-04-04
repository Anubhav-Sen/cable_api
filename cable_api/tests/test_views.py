import json
import shutil
from PIL import Image
from io import BytesIO
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from cable_api.factory import UserFactory
from cable_api.serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestUsersView(APITestCase):
    """
    A class to test the "api/users/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory  
        self.user_objects = self.user_factory.create_batch(5)
        self.maxDiff = None

    def test_users_GET(self):
        """
        A method to test the GET method of the "api/users/" endpoint.
        """
        endpoint = reverse('users')

        users_list = []

        for user in self.user_objects:

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

        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')

        tmp_file = SimpleUploadedFile("file.jpg", bts.getvalue(), content_type="image/jpg")
        
        request_dict = {
            'user_name': 'test',
            'email_address': 'test@test.com',
            'profile_image': tmp_file,
            'password': 'test_password',
        }

        response = self.client.post(endpoint, request_dict, format='multipart')

        new_user = get_user_model().objects.filter(user_name = 'test').first()

        user_serializer = UserSerializer(new_user)

        expected_response = {'new_user': user_serializer.data}

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        self.user_factory.reset_sequence()

        shutil.rmtree('cable_api/tests/media')

class TestUserViewNoAuth(APITestCase):
    """
    A class to test the "api/users/user_id" endpoint for methods where authentication isn't needed.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory()
        self.maxDiff = None

    def test_user_view_no_auth_GET(self):
        """
        A method to test the GET method of the "api/users/user_id" endpoint.
        """
        endpoint = reverse('user', kwargs={'user_id': self.user_factory.id})

        user_dict = {
            'id': self.user_factory.id,
            'user_name': self.user_factory.user_name,
            'email_address': self.user_factory.email_address,
            'profile_image': self.user_factory.profile_image.url,
        }

        expected_response = {'user': user_dict}

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))