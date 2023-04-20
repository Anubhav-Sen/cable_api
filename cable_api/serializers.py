from rest_framework import serializers
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant, Message

class UserSerializer(serializers.ModelSerializer):
    """
    A class to:
      - Serialize the fields of the user model into a python dictionary.
      - Validate data passed to it. 
    """
    class Meta:

        model = get_user_model()

        fields = [
            'id',
            'user_name',
            'email_address',
            'profile_image',
            'password',
        ]
        
        extra_kwargs = {
            'id':{'read_only': True, 'required': False, 'allow_null': True},
            'password': {'write_only': True}
            }

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    A class to:
      - Serialize the editable fields of the user model into a python dictionary.
      - Validate data passed to it. 
    """
    class Meta:

        model = get_user_model()

        fields = [
            'user_name',
            'profile_image',
            'password'
        ]

        extra_kwargs = {
            'user_name': {'required': False, 'allow_null': True},
            'profile_image': {'required': False, 'allow_null': True},
            'password': {'required': False, 'allow_null': True}
        }

class ParticipantingUserSerializer(serializers.ModelSerializer):
    """
    A class to:
      - Serialize the model user field of the paticipant model into a python dictionary.
      - Validate data passed to it. 
    """
    model_user = UserSerializer()

    class Meta:

        model = Participant

        fields = ['model_user'] 

class ChatSerializer(serializers.ModelSerializer):
    """
    A class to:
      - Serialize the fields of the chat model into a python dictionary with an additional field containing chat participants.
      - Validate data passed to it.  
    """
    participants = ParticipantingUserSerializer(required=False, many=True)
    
    class Meta:

        model = Chat

        fields = [   
            'id',
            'display_name',
            'participants'
        ]

        extra_kwargs = {
            'id':{'read_only': True, 'required': False, 'allow_null': True},
            }
        
class MessageSerializer(serializers.ModelSerializer):
    """
    - Serialize the fields of the message model into a python dictionary.
    - Validate data passed to it.  
    """
    class Meta:
        model = Message
        fields = [
            'id',
            'content',  
            'chat',
            'sender',
            'date_created'
        ]

    extra_kwargs = {
        'id':{'read_only': True, 'required': False, 'allow_null': True},
        'chat':{'read_only': True, 'required': False, 'allow_null': True},
        'sender':{'read_only': True, 'required': False, 'allow_null': True},
        'date_created':{'read_only': True, 'required': False, 'allow_null': True},
    }
    
class EmailSerializer(serializers.Serializer):
    """
    A class to:
      - Serialize the email passed to it into a python dictionary.
      - Validate the email passed to it.  
    """
    email_address = serializers.EmailField(max_length=255, write_only=True, required=True)

