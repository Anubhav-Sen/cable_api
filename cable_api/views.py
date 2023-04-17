from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant
from cable_api.serializers import UserSerializer, UserUpdateSerializer, ChatSerializer

@api_view(['GET', 'POST'])
def users_view(request):
    """
    A function that defines the "api/users/" endpoint.
    """
    if request.method == 'GET':

        users = get_user_model().objects.all()

        users_serializer = UserSerializer(users, many=True)

        response_dict = {'users': users_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == "POST":

        user_serializer = UserSerializer(data=request.data)

        if user_serializer.is_valid(raise_exception=True):
            
            new_user = get_user_model().objects.create_user(**user_serializer.validated_data)

            user_serializer = UserSerializer(new_user)

            response_dict = {'new_user': user_serializer.data}
                                    
            return Response(response_dict, status=status.HTTP_201_CREATED)
        
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def user_view(request, user_id):
    """
    A function that defines the methods of the "api/users/user_id" endpoint.
    """    
    if request.method == 'GET':

        user = get_user_model().objects.filter(id = user_id).first()

        if user == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)

        user_serializer = UserSerializer(user)

        response_dict = {'user': user_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        
        user = get_user_model().objects.filter(id = user_id).first()

        if user == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        elif request.user.id != user_id:

            response_dict = {'detail': 'Unauthorized to make changes to this object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)

        update_serializer = UserUpdateSerializer(data=request.data)  

        if update_serializer.is_valid(raise_exception=True):
            
            for key, value in update_serializer.validated_data.copy().items():
                
                if value == None:

                    update_serializer.validated_data.pop(key)
                        
            get_user_model().objects.filter(id = user_id).update(**update_serializer.validated_data)

            updated_user = get_user_model().objects.get(id = user_id)       

            user_serializer = UserSerializer(updated_user)    

            response_dict = {'updated_user': user_serializer.data} 
      
            return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':

        user = get_user_model().objects.filter(id = user_id).first()

        if user == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)
    
def chats_view(request):
    """
    A function that defines the "api/chats/" endpoint.
    """
    if request.method == 'GET':

        chats = Chat.objects.filter(participants__model_user = request.user).all()

        chat_serializer = ChatSerializer(chats, many=True)

        if chat_serializer.is_valid(raise_exception=True):

            response_dict = {'chats': chat_serializer.data}