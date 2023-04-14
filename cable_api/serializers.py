from rest_framework import serializers
from django.contrib.auth import get_user_model

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
            'id':{'read_only': True},
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