import json
import shutil
from PIL import Image
from io import BytesIO
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from cable_api.factory import UserFactory, ChatFactory, ParticipantFactory, MessageFactory
from cable_api.serializers import UserSerializer, ChatSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant, Message
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime

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
    A class to test the "api/users/user_id/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
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

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        self.user_factory.reset_sequence()
        self.chat_factory.reset_sequence()
        self.participant_factory.reset_sequence()

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
        self.auth_user = UserFactory.create()
        self.test_user = UserFactory.create()
        self.chat_object = ChatFactory.create()
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
class TestMessagesView(APITestCase):
    """
    A class to test the "api/chats/chat_id/messages/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
        self.test_user = UserFactory.create()
        self.chat_object = ChatFactory.create()
        self.participant_factory = ParticipantFactory
        self.participant_one = self.participant_factory(model_user = self.auth_user, chat = self.chat_object)
        self.participant_two = self.participant_factory(model_user = self.test_user, chat = self.chat_object)
        self.message_factory = MessageFactory
        self.message_objects = self.message_factory.create_batch(5, sender = self.auth_user, chat = self.chat_object)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_messages_view_GET(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/" endpoint.
        """
        endpoint = reverse('messages', kwargs={'chat_id': self.chat_object.id})

        messages = []

        for message in self.message_objects:

            message_dict = {
                'id': message.id,
                'content': message.content,
                'sender': message.sender.id,  
                'chat': message.chat.id,
                'date_created': message.date_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            }

            messages.append(message_dict)

        expected_response = {'messages': messages}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_messages_view_POST(self):
        """
        A method to test the POST method of the "api/chats/chat_id/messages/" endpoint.
        """
        endpoint = reverse('messages', kwargs={'chat_id': self.chat_object.id})

        request_dict = {
            'content': 'test message',
        }

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        new_message = Message.objects.filter(content = 'test message').first()

        message_serializer = MessageSerializer(new_message)

        expected_response = {'new_message': message_serializer.data}

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        self.participant_factory.reset_sequence()
        self.message_factory.reset_sequence()

        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestMessagesView(APITestCase):
    """
    A class to test the "api/chats/chat_id/messages/message_id/" endpoint.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.auth_user = UserFactory.create()
        self.test_user = UserFactory.create()
        self.chat_object = ChatFactory.create()
        self.participant_factory = ParticipantFactory
        self.participant_one = self.participant_factory(model_user = self.auth_user, chat = self.chat_object)
        self.participant_two = self.participant_factory(model_user = self.test_user, chat = self.chat_object)
        self.message_object = MessageFactory.create(sender = self.auth_user, chat = self.chat_object)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_message_view_GET(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/message_id/" endpoint.
        """
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object.id, 'message_id': self.message_object.id})

        message_dict = {
            'id': self.message_object.id,
            'content': self.message_object.content,
            'sender': self.message_object.sender.id,  
            'chat': self.message_object.chat.id,
            'date_created': self.message_object.date_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        expected_response = {'message': message_dict}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_view_PATCH(self):
        """
        A method to test the patch method of the "api/chats/chat_id/messages/message_id/" endpoint.
        """
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object.id, 'message_id': self.message_object.id})

        request_dict = {
            'content': 'updated message'
        }

        message_dict = {
            'id': self.message_object.id,
            'content': 'updated message',
            'sender': self.message_object.sender.id,  
            'chat': self.message_object.chat.id,
            'date_created': self.message_object.date_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        expected_response = {'updated_message': message_dict}

        response = self.client.patch(endpoint, request_dict, **self.auth_headers)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_view_DELETE(self):
        """
        A method to test the delete method of the "api/chats/chat_id/messages/message_id/" endpoint.
        """
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object.id, 'message_id': self.message_object.id})
        
        expected_response = {'detail': 'This object has been deleted.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        message = Message.objects.filter(id = self.message_object.id).first()

        self.assertEqual(None, message)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        self.participant_factory.reset_sequence()

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
        A method to test the GET method of the "api/users/user_id/" endpoint while no users exist.
        """
        endpoint = reverse('user', kwargs={'user_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.get(endpoint)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_PATCH(self):
        """
        A method to test the PATCH method of the "api/users/user_id/" endpoint while no users exist.
        """
        endpoint = reverse('user', kwargs={'user_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.patch(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_user_DELETE(self):
        """
        A method to test the DELETE method of the "api/users/user_id/" endpoint while no users exist.
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
        A method to test the GET method of the "api/chats/" endpoint while no users exist.
        """
        endpoint = reverse('chats')

        expected_response = {'detail': 'These objects do not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chats_POST(self):
        """
        A method to test the POST method of the "api/chats/" endpoint while no users exist.
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
        A method to test the GET method of the "api/chats/chat_id/" endpoint while no users exist.
        """
        endpoint = reverse('chat', kwargs={'chat_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_chat_PATCH(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/" endpoint while no users exist.
        """
        endpoint = reverse('chat', kwargs={'chat_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.patch(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_chat_DELETE(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/" endpoint while no users exist.
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