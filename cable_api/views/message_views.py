from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cable_api.models import Chat, Message
from cable_api.serializers import MessageSerializer
from cable_api.views.view_helpers import *
              
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  
def messages_view(request, chat_id):
    """
    A function that defines the "api/chats/chat_id/messages/" endpoint.
    """
    if request.method == 'GET':
        
        chat = get_object_or_404(Chat, id = chat_id)
        
        check_object_perms(chat, participants__model_user = request.user)

        messages = get_object_list_or_404(Message, chat = chat)
            
        message_serializer = MessageSerializer(messages, many=True)
        
        response_dict = {'messages': message_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)

    if request.method == 'POST':

        message_serializer = MessageSerializer(data=request.data)
        message_serializer.is_valid(raise_exception=True)

        chat = get_object_or_404(Chat, id = chat_id)
        
        check_object_perms(chat, participants__model_user = request.user)
        
        new_message = Message.objects.create(sender = request.user, chat = chat, **message_serializer.validated_data)
        
        message_serializer = MessageSerializer(new_message)

        response_dict = {'new_message': message_serializer.data}
                                
        return Response(response_dict, status=status.HTTP_201_CREATED)
    
@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])  
def message_view(request, chat_id, message_id):
    """
    A function that defines the "api/chats/chat_id/messages/message_id/" endpoint.
    """
    if request.method == 'GET':

        chat = get_object_or_404(Chat, id = chat_id)
        
        check_object_perms(chat, participants__model_user = request.user)

        message = get_object_or_404(Message, id = message_id)
        
        check_object_perms(message, chat = chat)
                
        message_serializer = MessageSerializer(message)

        response_dict = {'message': message_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    if request.method == 'PATCH':

        message_serializer = MessageSerializer(data=request.data)
        message_serializer.is_valid(raise_exception=True)

        chat = get_object_or_404(Chat, id = chat_id)
        
        check_object_perms(chat, participants__model_user = request.user)

        message = get_object_or_404(Message, id = message_id)
        
        check_object_perms(message, chat = chat)    

        update_data = clean_serializer_data(message_serializer.validated_data)    
        
        Message.objects.filter(id = message_id).update(**update_data)
        
        updated_message = Message.objects.get(id = message_id)   

        message_serializer = MessageSerializer(updated_message)    

        response_dict = {'updated_message': message_serializer.data} 
    
        return Response(response_dict, status=status.HTTP_200_OK)
    
    if request.method == 'DELETE':

        chat = get_object_or_404(Chat, id = chat_id)
        
        check_object_perms(chat, participants__model_user = request.user)

        message = get_object_or_404(Message, id = message_id)
        
        check_object_perms(message, chat = chat)   
        
        message.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)    