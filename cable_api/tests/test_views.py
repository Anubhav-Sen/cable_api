import json
import shutil
from PIL import Image
from io import BytesIO
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from cable_api.factory import UserFactory, ChatFactory, ParticipantFactory
from cable_api.serializers import UserSerializer
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant
from django.core.files.uploadedfile import SimpleUploadedFile

def get_auth_headers(client, user):
        """
        A function to get authentiation headers.
        """ 
        auth_endpoint = reverse('token_obtain_pair')

        auth_credentials = {
            'email_address': user.email_address,
            'password': 'testpassword'
        }
    
        auth_response = client.post(auth_endpoint, auth_credentials)

        auth_headers = {'HTTP_AUTHORIZATION':f'Bearer {json.loads(auth_response.content)["access"]}'}

        return auth_headers

def create_temp_image(filename = 'file'):
    """
    A function to create a temporary in memory image file.
    """
    bts = BytesIO()
    img = Image.new('RGB', (100, 100))
    img.save(bts, 'jpeg')

    temp_file = SimpleUploadedFile(f'{filename}.jpg', bts.getvalue(), content_type='image/jpg')

    return temp_file

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

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestUserView(APITestCase):
    """
    A class to test the "api/users/user_id" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_object = UserFactory.create()
        self.auth_headers = get_auth_headers(self.client, self.user_object)
        self.maxDiff = None

    def test_user_view_GET(self):
        """
        A method to test the GET method of the "api/users/user_id" endpoint.
        """
        endpoint = reverse('user', kwargs={'user_id': self.user_object.id})

        user_dict = {
            'id': self.user_object.id,
            'user_name': self.user_object.user_name,
            'email_address': self.user_object.email_address,
            'profile_image': self.user_object.profile_image.url,
        }

        expected_response = {'user': user_dict}

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_view_PATCH(self):
        """
        A method to test the PATCH method of the "api/users/user_id" endpoint.
        """
        endpoint = reverse('user', kwargs={'user_id': self.user_object.id})

        profile_image = create_temp_image('updated_profile_image')
        
        request_dict = {
            'user_name': 'updated_username',
            'profile_image': profile_image,
            'password': 'updated_password',
        }

        user_dict = {
            'id': self.user_object.id,
            'user_name': 'updated_username',
            'email_address': self.user_object.email_address,
            'profile_image': '/media/updated_profile_image.jpg',
        }
 
        expected_response = {'updated_user': user_dict}

        response = self.client.patch(endpoint, request_dict, format='multipart', **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_user_view_DELETE(self):
        """
        A method to test the DELETE method of the "api/users/user_id" endpoint.
        """ 
        endpoint = reverse('user', kwargs={'user_id': self.user_object.id})

        expected_response = {'detail': 'This object has been deleted.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        user = get_user_model().objects.filter(id = self.user_object.id).first()

        self.assertEqual(None, user)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')

class TestChatsView(APITestCase):
    """
    A class to test the "api/chats/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory
        self.chat_factory = ChatFactory
        self.participant_factory = ParticipantFactory
        self.maxDiff = None

        for index in range(5):

            participant_one = self.user_factory.create()
            participant_two = self.user_factory.create()
            chat = self.chat_factory.create()

            self.participant_factory(model_user = participant_one, chat = chat)
            self.participant_factory(model_user = participant_two, chat = chat)

    def test_chats_view_GET(self):

        participants = Participant.objects.all()

        print(participants)