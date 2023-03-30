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