from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.serializers import UserSerializer

@api_view(['GET', 'POST'])
def users(request):
    """
    A function that defines the "api/users/" endpoint.
    """

    if request.method == 'GET':

        users = get_user_model().objects.all()

        users_serializer = UserSerializer(users, many=True)

        response_dict = {'users': users_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == "POST":

        users_serializer = UserSerializer(data=request.data)

        if users_serializer.is_valid():
            
            return Response({'test':'test'}, status=status.HTTP_201_CREATED)
