import json
import shutil
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from cable_api.factory import UserFactory, ChatFactory, ParticipantFactory, MessageFactory
from cable_api.serializers import  MessageSerializer
from cable_api.models import Message
from cable_api.tests.helpers import get_auth_headers

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
class TestMessagesWhenObjectsDontExist(APITestCase):
    """
    A class to test the "api/chats/chat_id/messages/" endpoint when required objects don't exist.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory
        self.chat_factory = ChatFactory
        self.paticipant_factory = ParticipantFactory
        self.auth_user = self.user_factory.create()
        self.chat_object = self.chat_factory.create()
        self.user_object = self.user_factory.create()
        self.paticipant_factory.create(model_user = self.user_object, chat = self.chat_object)
        self.paticipant_factory.create(model_user = self.auth_user, chat = self.chat_object)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_messages_GET_no_chat(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/" endpoint while no chat exists.
        """
        endpoint = reverse('messages', kwargs={'chat_id': '0'})

        expected_response = {'detail': 'These objects do not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_messages_GET_no_messages(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/" endpoint while no messages exists.
        """
        endpoint = reverse('messages', kwargs={'chat_id': self.chat_object.id})

        expected_response = {'detail': 'These objects do not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_messages_POST_no_chat(self):
        """
        A method to test the POST method of the "api/chats/chat_id/messages/" endpoint while no messages exists.
        """
        endpoint = reverse('messages', kwargs={'chat_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        request_dict = {
            'content': 'test message',
        }

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
        
    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestMessagesAgainstUnauthorizedUser(APITestCase):
    """
    A class to test the "api/chats/chat_id/messages" endpoint against an unauthorized user.
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

    def test_messages_view_GET_unauthorized_user(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages" on protected messages without correct credentials.
        """ 
        endpoint = reverse('messages', kwargs={'chat_id': self.chat_object.id})
            
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_messages_view_POST_unauthorized_user(self):
        """
        A method to test the POST method of the "api/chats/chat_id/messages" on protected messages without correct credentials.
        """ 
        endpoint = reverse('messages', kwargs={'chat_id': self.chat_object.id})

        request_dict = {
            'content': 'test message'
        }
            
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.post(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
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

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestMessageWhenObjectsDontExist(APITestCase):
    """
    A class to test the "api/chats/chat_id/messages/message_id/" endpoint when required objects don't exist.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory
        self.chat_factory = ChatFactory
        self.paticipant_factory = ParticipantFactory
        self.auth_user = self.user_factory.create()
        self.chat_object = self.chat_factory.create()
        self.user_object = self.user_factory.create()
        self.paticipant_factory.create(model_user = self.user_object, chat = self.chat_object)
        self.paticipant_factory.create(model_user = self.auth_user, chat = self.chat_object)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None

    def test_message_GET_no_chat(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/message_id/" endpoint while no chat exists.
        """
        endpoint = reverse('message', kwargs={'chat_id': '0', 'message_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_GET_no_message(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/message_id/" endpoint while no messages exists.
        """
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object.id, 'message_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_PATCH_no_chat(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/messages/message_id/" endpoint while no chat exists.
        """
        endpoint = reverse('message', kwargs={'chat_id': '0', 'message_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        request_dict = {
            'content': 'test message',
        }

        response = self.client.patch(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_message_PATCH_no_message(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/messages/message_id/" endpoint while no chat exists.
        """
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object.id, 'message_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        request_dict = {
            'content': 'test message',
        }

        response = self.client.patch(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_DELETE_no_chat(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/messages/message_id/" endpoint while no chat exists.
        """
        endpoint = reverse('message', kwargs={'chat_id': '0', 'message_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        request_dict = {
            'content': 'test message',
        }

        response = self.client.delete(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_message_DELETE_no_message(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/messages/message_id/" endpoint while no chat exists.
        """
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object.id, 'message_id': '0'})

        expected_response = {'detail': 'This object does not exist.'}

        request_dict = {
            'content': 'test message',
        }

        response = self.client.delete(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
        
    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')

@override_settings(MEDIA_ROOT = 'cable_api/tests/media')
class TestMessageAgainstUnauthorizedUser(APITestCase):
    """
    A class to test the "api/chats/chat_id/messages/message_id" endpoint against an unauthorized user.
    """
    def setUp(self):
        """
        A method to define the base setup for this test class.
        """
        self.user_factory = UserFactory
        self.chat_factory = ChatFactory
        self.participant_factory = ParticipantFactory
        self.message_factory = MessageFactory
        self.auth_user = self.user_factory.create()
        self.test_user_1 = self.user_factory.create()
        self.test_user_2 = self.user_factory.create()
        self.chat_object_1 = self.chat_factory.create()
        self.participant_factory(model_user = self.test_user_1, chat = self.chat_object_1)
        self.participant_factory(model_user = self.test_user_2, chat = self.chat_object_1)
        self.chat_object_2 = self.chat_factory.create()
        self.participant_factory(model_user = self.auth_user, chat = self.chat_object_2)
        self.participant_factory(model_user = self.test_user_1, chat = self.chat_object_2)
        self.message_1 = self.message_factory.create(sender = self.test_user_1, chat=self.chat_object_1)
        self.message_2 = self.message_factory.create(sender = self.test_user_1, chat=self.chat_object_2)
        self.auth_headers = get_auth_headers(self.client, self.auth_user)
        self.maxDiff = None
    
    def test_message_view_GET_unauthorized_user_chat(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/message_id" on protected message without correct credentials to access the parent chat.
        """ 
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object_1.id, 'message_id': self.message_1.id})
            
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_view_GET_unauthorized_user_message(self):
        """
        A method to test the GET method of the "api/chats/chat_id/messages/message_id" on protected message without correct credentials.
        """ 
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object_1.id, 'message_id': self.message_1.id})
            
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.get(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))
    
    def test_message_view_PATCH_unauthorized_user_chat(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/messages/message_id" on protected message without correct credentials to access the parent chat.
        """ 
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object_1.id, 'message_id': self.message_1.id})

        request_dict = {
            'content': 'test message'
        }   

        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.patch(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_view_PATCH_unauthorized_user_message(self):
        """
        A method to test the PATCH method of the "api/chats/chat_id/messages/message_id" on protected message without correct credentials.
        """ 
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object_1.id, 'message_id': self.message_1.id})
            
        request_dict = {
            'content': 'test message'
        }   

        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.patch(endpoint, request_dict, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_view_DELETE_unauthorized_user_chat(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/messages/message_id" on protected message without correct credentials to access the parent chat.
        """ 
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object_1.id, 'message_id': self.message_1.id})
            
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def test_message_view_DELETE_unauthorized_user_message(self):
        """
        A method to test the DELETE method of the "api/chats/chat_id/messages/message_id" on protected message without correct credentials.
        """ 
        endpoint = reverse('message', kwargs={'chat_id': self.chat_object_1.id, 'message_id': self.message_1.id})
            
        expected_response = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

        response = self.client.delete(endpoint, **self.auth_headers)

        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual(expected_response, json.loads(response.content))

    def tearDown(self):
        """
        A method to delete data and revert the changes made using the setup method after each test run.
        """
        shutil.rmtree('cable_api/tests/media')