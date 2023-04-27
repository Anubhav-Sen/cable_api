import json
import shutil
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from cable_api.factory import UserFactory
from cable_api.serializers import UserSerializer
from django.contrib.auth import get_user_model
from cable_api.tests.test_helpers import get_auth_headers, create_temp_image

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

        profile_image = create_temp_image()
       
        request_dict = {
            'user_name': 'test',
            'email_address': 'test@test.com',
            'profile_image': profile_image,
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

class TestUsersWhenObjectsDontExist(APITestCase):
    """
    A class to test the "api/users/" endpoint when required objects don't exist.
    """
    def test_users_GET(self):
        """
        A method to test the GET method of the "api/users/" endpoint while no users exist.
        """
        endpoint = reverse('users')

        expected_response = {'detail': 'These objects do not exist.'}

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestUserView(APITestCase):
    """
    A class to test the "api/users/user_id/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
        self.user_object = UserFactory.create()
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_user_view_GET(self):
        """
        A method to test the GET method of the "api/users/user_id/" endpoint.
        """
        endpoint = reverse('user', kwargs={'user_id': self.auth_user.id})

        user_dict = {
            'id': self.auth_user.id,
            'user_name': self.auth_user.user_name,
            'email_address': self.auth_user.email_address,
            'profile_image': self.auth_user.profile_image.url,
        }

        expected_response = {'user': user_dict}

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_view_PATCH(self):
        """
        A method to test the PATCH method of the "api/users/user_id/" endpoint.
        """
        endpoint = reverse('user', kwargs={'user_id': self.auth_user.id})

        profile_image = create_temp_image('updated_profile_image')
        
        request_dict = {
            'user_name': 'updated_username',
            'profile_image': profile_image,
            'password': 'updated_password',
        }

        user_dict = {
            'id': self.auth_user.id,
            'user_name': 'updated_username',
            'email_address': self.auth_user.email_address,
            'profile_image': '/media/updated_profile_image.jpg',
        }
 
        expected_response = {'updated_user': user_dict}

        response = self.client.patch(endpoint, request_dict, format='multipart', **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
        
    def test_user_view_DELETE(self):
        """
        A method to test the DELETE method of the "api/users/user_id/" endpoint.
        """ 
        endpoint = reverse('user', kwargs={'user_id': self.auth_user.id})

        expected_response = {'detail': 'This object has been deleted.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        user = get_user_model().objects.filter(id = self.auth_user.id).first()

        self.assertEqual(None, user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestUserWhenObjectsDontExist(APITestCase):
    """
    A class to test the "api/users/user_id/" endpoint when required objects don't exist.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_user_GET(self):
        """
        A method to test the GET method of the "api/users/user_id/" endpoint while no user exist.
        """
        endpoint = reverse('user', kwargs={'user_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_PATCH(self):
        """
        A method to test the PATCH method of the "api/users/user_id/" endpoint while no user exist.
        """
        endpoint = reverse('user', kwargs={'user_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.patch(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_DELETE(self):
        """
        A method to test the DELETE method of the "api/users/user_id/" endpoint while no user exist.
        """
        endpoint = reverse('user', kwargs={'user_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestUserAgainstUnauthorizedUser(APITestCase):
    """
    A class to test the "api/users/user_id/" endpoint against an unauthorized user.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory
        self.auth_user = self.user_factory.create()
        self.user_object = self.user_factory.create()
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_user_view_PATCH_unauthorized_user(self):
        """
        A method to test the PATCH method of the "api/users/user_id/" on a protected user without correct credentials.
        """ 
        endpoint = reverse('user', kwargs={'user_id': self.user_object.id})
        
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.patch(endpoint, format='multipart', **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_view_DELETE_unauthorized_user(self):
        """
        A method to test the DELETE method of the "api/users/user_id/" on a protected user without correct credentials.
        """ 
        endpoint = reverse('user', kwargs={'user_id': self.user_object.id})
        
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.delete(endpoint, format='multipart', **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')