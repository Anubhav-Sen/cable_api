from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant
from cable_api.serializers import ChatSerializer, EmailSerializer
from cable_api.views.view_helpers import *

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  
def chats_view(request):
    """
    A function that defines the "api/chats/" endpoint.
    """
    if request.method == 'GET':

        chats = get_object_list_or_404(Chat, participants__model_user = request.user)

        chat_serializer = ChatSerializer(chats, many=True)
        
        response_dict = {'chats': chat_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':

        email_serializer = EmailSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)

        chat_serializer = ChatSerializer(data=request.data)
        chat_serializer.is_valid(raise_exception=True)

        chat_user = get_object_or_404(get_user_model(), email_address = email_serializer.validated_data['email_address'])

        compare_email(email_serializer.validated_data['email_address'], request.user.email_address)
        
        check_chat_exists(chat_user, request.user)

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
    A function that defines the "api/chats/chat_id/" endpoint.
    """
    if request.method == 'GET':

        chat = get_object_or_404(Chat, id = chat_id)
        check_object_perms(chat, participants__model_user = request.user)
           
        chat_serializer = ChatSerializer(chat)

        response_dict = {'chat': chat_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':

        chat_serializer = ChatSerializer(data=request.data)  
        chat_serializer.is_valid(raise_exception=True)
        
        chat = get_object_or_404(Chat, id = chat_id)
        
        check_object_perms(chat, participants__model_user = request.user)

        update_data = clean_serializer_data(chat_serializer.validated_data)            
                    
        Chat.objects.filter(id = chat_id).update(**update_data)
        
        updated_chat = Chat.objects.get(id = chat_id)       

        chat_serializer = ChatSerializer(updated_chat)    

        response_dict = {'updated_chat': chat_serializer.data} 
    
        return Response(response_dict, status=status.HTTP_200_OK)   
    
    elif request.method == 'DELETE':
        
        chat = get_object_or_404(Chat, id = chat_id)

        check_object_perms(chat, participants__model_user = request.user)
        
        chat.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)