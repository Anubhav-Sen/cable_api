import json
import shutil
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from cable_api.factory import UserFactory, ChatFactory, ParticipantFactory
from cable_api.serializers import ChatSerializer
from cable_api.models import Chat, Participant
from cable_api.tests.test_helpers import get_auth_headers

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
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
        self.auth_user = self.user_factory.create()
        self.test_user = self.user_factory.create()
        self.user_objects = self.user_factory.create_batch(5)
        self.chat_objects = self.chat_factory.create_batch(5)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None
        
        for index in range(5):

            self.participant_factory(model_user = self.auth_user, chat = self.chat_objects[index])
            self.participant_factory(model_user = self.user_objects[index], chat = self.chat_objects[index])
        
    def test_chats_view_GET(self):
        """
        A method to test the GET method of the "api/chats/" endpoint.
        """ 
        endpoint = reverse('chats')

        chats = []

        for index in range(5):

            participant_one = {
                'id': self.auth_user.id,
                'user_name': self.auth_user.user_name,
                'email_address': self.auth_user.email_address,
                'profile_image': self.auth_user.profile_image.url,
            }

            participant_two = {
                'id': self.user_objects[index].id,
                'user_name': self.user_objects[index].user_name,
                'email_address': self.user_objects[index].email_address,
                'profile_image': self.user_objects[index].profile_image.url,
            }

            participants = [{'model_user': participant_one}, {'model_user': participant_two}]      

            chat = {
                'id': self.chat_objects[index].id,
                'display_name': self.chat_objects[index].display_name,
                'participants': participants
            }

            chats.append(chat)

        expected_response = {'chats': chats}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chats_view_POST(self):
        """
        A method to test the POST method of the "api/chats/" endpoint.
        """ 
        endpoint = reverse('chats')

        request_dict = {
            'display_name': 'test_chat',
            'email_address': self.test_user.email_address
        }

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        new_chat = Chat.objects.filter(display_name = 'test_chat').first()

        chat_serializer = ChatSerializer(new_chat)

        expected_response = {'new_chat': chat_serializer.data}

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chats_view_POST_same_email_as_auth_user(self):
        """
        A method to test the POST method of the "api/chats/" endpoint when the email passed in is the same as the authenticated user.
        """ 
        endpoint = reverse('chats')

        request_dict = {
            'display_name': 'test_chat',
            'email_address': self.auth_user.email_address
        }

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        expected_response = {'detail': "Email provided cannot be the same as the authenticated user's."}

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chats_view_POST_while_chat_already_exists(self):
        """
        A method to test the POST method of the "api/chats/" endpoint when the chat being created already exists.
        """ 
        endpoint = reverse('chats')

        chat_object = self.chat_factory.create()

        self.participant_factory(model_user = self.auth_user, chat = chat_object)
        self.participant_factory(model_user = self.test_user, chat = chat_object)

        request_dict = {
            'display_name': 'test_chat',
            'email_address': self.test_user.email_address
        }

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        expected_response = {'detail': 'This object already exists.'}

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        self.user_factory.reset_sequence()
        self.chat_factory.reset_sequence()
        self.participant_factory.reset_sequence()

        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestChatsWhenObjectsDontExist(APITestCase):
    """
    A class to test the "api/chats/" endpoint when required objects don't exist.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_chats_GET(self):
        """
        A method to test the GET method of the "api/chats/" endpoint while no chats exist.
        """
        endpoint = reverse('chats')

        expected_response = {'detail': 'These objects do not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chats_POST(self):
        """
        A method to test the POST method of the "api/chats/" endpoint while no chats exist.
        """
        endpoint = reverse('chats')

        expected_response = {'detail': 'This object does not exist.'}

        request_dict = {
            'display_name': 'test_chat',
            'email_address': 'test@test.com'
        }

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestChatView(APITestCase):
    """
    A class to test the "api/chats/chat_id/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """

        self.user_factory = UserFactory
        self.chat_factory = ChatFactory
        self.auth_user = self.user_factory.create()
        self.test_user = self.user_factory.create()
        self.chat_object = self.chat_factory.create()
        self.participant_factory = ParticipantFactory
        self.participant_one = self.participant_factory(model_user = self.auth_user, chat = self.chat_object)
        self.participant_two = self.participant_factory(model_user = self.test_user, chat = self.chat_object)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_chat_view_GET(self):
        """
        A method to test the GET method of the "api/chats/chat_id/" endpoint.
        """
        endpoint = reverse('chat', kwargs={'chat_id': self.chat_object.id})

        participant_one = {
            'id': self.auth_user.id,
            'user_name': self.auth_user.user_name,
            'email_address': self.auth_user.email_address,
            'profile_image': self.auth_user.profile_image.url,
            }

        participant_two = {
            'id': self.test_user.id,
            'user_name': self.test_user.user_name,
            'email_address': self.test_user.email_address,
            'profile_image': self.test_user.profile_image.url,
        }

        participants = [{'model_user': participant_one}, {'model_user': participant_two}]      

        chat_dict = {
            'id': self.chat_object.id,
            'display_name': self.chat_object.display_name,
            'participants': participants
        }

        expected_response = {'chat': chat_dict}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chat_view_PATCH(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/" endpoint.
        """
        endpoint = reverse('chat', kwargs={'chat_id': self.chat_object.id})
        
        request_dict = {
            'display_name': 'updated_name'
        }

        participant_one = {
                'id': self.auth_user.id,
                'user_name': self.auth_user.user_name,
                'email_address': self.auth_user.email_address,
                'profile_image': self.auth_user.profile_image.url,
            }

        participant_two = {
            'id': self.test_user.id,
            'user_name': self.test_user.user_name,
            'email_address': self.test_user.email_address,
            'profile_image': self.test_user.profile_image.url,
        }

        participants = [{'model_user': participant_one}, {'model_user': participant_two}]      

        chat_dict = {
            'id': self.chat_object.id,
            'display_name': 'updated_name',
            'participants': participants
        }
 
        expected_response = {'updated_chat': chat_dict}

        response = self.client.patch(endpoint, request_dict, format='multipart', **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_view_DELETE(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/" endpoint.
        """ 
        endpoint = reverse('chat', kwargs={'chat_id': self.chat_object.id})

        expected_response = {'detail': 'This object has been deleted.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        chat = Chat.objects.filter(id = self.chat_object.id).first()

        participant_one = Participant.objects.filter(id = self.participant_one.id).first()
        
        participant_two = Participant.objects.filter(id = self.participant_two.id).first()

        self.assertEqual(None, chat)
        self.assertEqual(None, participant_one)
        self.assertEqual(None, participant_two)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        self.participant_factory.reset_sequence()

        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestChatWhenObjectsDontExist(APITestCase):
    """
    A class to test the "api/chats/chat_id/" endpoint when required objects don't exist.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_chat_GET(self):
        """
        A method to test the GET method of the "api/chats/chat_id/" endpoint while no chat exist.
        """
        endpoint = reverse('chat', kwargs={'chat_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_chat_PATCH(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/" endpoint while no chat exist.
        """
        endpoint = reverse('chat', kwargs={'chat_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.patch(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chat_DELETE(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/" endpoint while no chat exist.
        """
        endpoint = reverse('chat', kwargs={'chat_id': '0'})

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
class TestChatAgainstUnauthorizedUser(APITestCase):
    """
    A class to test the "api/chats/chat_id/" endpoint against an unauthorized user.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory
        self.chat_factory = ChatFactory
        self.participant_factory = ParticipantFactory
        self.auth_user = self.user_factory.create()
        self.test_user_1 = self.user_factory.create()
        self.test_user_2 = self.user_factory.create()
        self.chat_object = self.chat_factory.create()
        self.participant_factory(model_user = self.test_user_1, chat = self.chat_object)
        self.participant_factory(model_user = self.test_user_2, chat = self.chat_object)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_chat_view_GET_unauthorized_user(self):
        """
        A method to test the GET method of the "api/chats/chat_id/" on a protected chat without correct credentials.
        """ 
        endpoint = reverse('chat', kwargs={'chat_id': self.chat_object.id})
        
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chat_view_PATCH_unauthorized_user(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/" on a protected chat without correct credentials.
        """ 
        endpoint = reverse('chat', kwargs={'chat_id': self.chat_object.id})
        
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.patch(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chat_view_DELETE_unauthorized_user(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/" on a protected chat without correct credentials.
        """ 
        endpoint = reverse('chat', kwargs={'chat_id': self.chat_object.id})
        
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')