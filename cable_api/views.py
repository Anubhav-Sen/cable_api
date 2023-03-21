from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.serializers import UserSerializer

@api_view(['GET'])
def users(request):
    """
    A function that defines the "api/users/" endpoint.
    """

    users = get_user_model().objects.all()

    users_serializer = UserSerializer(users, many=True)

    response_dict = {'users': users_serializer.data}

    return Response(response_dict, status=status.HTTP_200_OK)

@api_view(['GET'])
def test(request):
    return Response('test', status=status.HTTP_200_OK)    