from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):
    """
    A class to serializes the fields of the user model into a python dictionary.
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
        
        extra_kwargs = {'password': {'write_only': True}}