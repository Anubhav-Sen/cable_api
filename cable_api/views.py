from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant
from cable_api.serializers import UserSerializer, UserUpdateSerializer, ChatSerializer, EmailSerializer

@api_view(['GET', 'POST'])
def users_view(request):
    """
    A function that defines the "api/users/" endpoint.
    """
    if request.method == 'GET':

        users = get_user_model().objects.all()

        if users == None:

            response_dict = {'detail': 'These objects do not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)

        users_serializer = UserSerializer(users, many=True)

        response_dict = {'users': users_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == "POST":

        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
            
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

        user_update_serializer = UserUpdateSerializer(data=request.data)  
        user_update_serializer.is_valid(raise_exception=True)
        
        user = get_user_model().objects.filter(id = user_id).first()

        if user == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        elif request.user.id != user_id:

            response_dict = {'detail': 'Unauthorized to make changes to this object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
            
        for key, value in user_update_serializer.validated_data.copy().items():
            
            if value == None:

                user_update_serializer.validated_data.pop(key)
                    
        get_user_model().objects.filter(id = user_id).update(**user_update_serializer.validated_data)

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

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  
def chats_view(request):
    """
    A function that defines the "api/chats/" endpoint.
    """
    if request.method == 'GET':

        chats = Chat.objects.filter(participants__model_user = request.user).all()

        if chats == None:

            response_dict = {'detail': 'These objects do not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)

        chat_serializer = ChatSerializer(chats, many=True)
        
        response_dict = {'chats': chat_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':

        email_serializer = EmailSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)

        chat_serializer = ChatSerializer(data=request.data)
        chat_serializer.is_valid(raise_exception=True)

        chat_user = get_user_model().objects.filter(email_address = email_serializer.validated_data['email_address']).first()

        existing_chat = Chat.objects.filter(participants__model_user = chat_user).filter(participants__model_user = request.user).first()

        if email_serializer.validated_data['email_address'] == request.user.email_address:

            response_dict = {'detail': "Email provided cannot be the same as the authenticated user's."}

            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        elif existing_chat:

            response_dict = {'detail': 'This object already exists.'}

            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        new_chat = Chat.objects.create(**chat_serializer.validated_data)

        Participant.objects.create(model_user = request.user, chat = new_chat)
        Participant.objects.create(model_user = chat_user, chat = new_chat)

        chat_serializer = ChatSerializer(new_chat)

        response_dict = {'new_chat': chat_serializer.data}

        return Response(response_dict, status=status.HTTP_201_CREATED)
    
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated]) 
def chat_view(request, chat_id):
    """
    A function that defines the "api/chat/chat_id" endpoint.
    """
    if request.method == 'GET':
        
        chat = Chat.objects.filter(id = chat_id).first()

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first()

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to access this object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
           
        chat_serializer = ChatSerializer(user_chat)

        response_dict = {'chat': chat_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':

        chat_serializer = ChatSerializer(data=request.data)  
        chat_serializer.is_valid(raise_exception=True)
        
        chat = Chat.objects.filter(id = chat_id).first()

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first()

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to access this object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
            
        for key, value in chat_serializer.validated_data.copy().items():
            
            if value == None:

                chat_serializer.validated_data.pop(key)
                    
        Chat.objects.filter(id = chat_id).update(**chat_serializer.validated_data)

        updated_chat = get_user_model().objects.get(id = chat_id)       

        chat_serializer = ChatSerializer(updated_chat)    

        response_dict = {'updated_chat': chat_serializer.data} 
    
        return Response(response_dict, status=status.HTTP_200_OK)   