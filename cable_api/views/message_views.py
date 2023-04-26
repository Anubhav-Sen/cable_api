from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cable_api.models import Chat, Message
from cable_api.serializers import MessageSerializer
              
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  
def messages_view(request, chat_id):
    """
    A function that defines the "api/chats/chat_id/messages/" endpoint.
    """
    if request.method == 'GET':

        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        user_chat_messages = Message.objects.filter(chat = user_chat).all() or None

        if chat == None:

            response_dict = {'detail': 'These objects do not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)

        if user_chat_messages == None:

            response_dict = {'detail': 'These objects do not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
            
        message_serializer = MessageSerializer(user_chat_messages, many=True)
        
        response_dict = {'messages': message_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)

    if request.method == 'POST':

        message_serializer = MessageSerializer(data=request.data)
        message_serializer.is_valid(raise_exception=True)

        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        new_message = Message.objects.create(sender = request.user, chat = user_chat, **message_serializer.validated_data)
        
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

        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        message = Message.objects.filter(id = message_id).first() or None

        chat_message = Message.objects.filter(chat = chat).filter(id = message_id).first() or None

        user_chat_message = Message.objects.filter(chat = user_chat).filter(id = message_id).first() or None
        
        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        if message == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat_message == None and message != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        message_serializer = MessageSerializer(user_chat_message)

        response_dict = {'message': message_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    if request.method == 'PATCH':

        message_serializer = MessageSerializer(data=request.data)
        message_serializer.is_valid(raise_exception=True)

        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        message = Message.objects.filter(id = message_id).first() or None

        chat_message = Message.objects.filter(chat = chat).filter(id = message_id).first() or None

        user_chat_message = Message.objects.filter(chat = user_chat).filter(id = message_id).first() or None

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        if message == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat_message == None and message != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        for key, value in message_serializer.validated_data.copy().items():
            
            if value == None:

                message_serializer.validated_data.pop(key)
        
        Message.objects.filter(id = message_id).update(**message_serializer.validated_data)
        
        updated_message = Message.objects.get(id = message_id)   

        message_serializer = MessageSerializer(updated_message)    

        response_dict = {'updated_message': message_serializer.data} 
    
        return Response(response_dict, status=status.HTTP_200_OK)
    
    if request.method == 'DELETE':

        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        message = Message.objects.filter(id = message_id).first() or None

        chat_message = Message.objects.filter(chat = chat).filter(id = message_id).first() or None

        user_chat_message = Message.objects.filter(chat = user_chat).filter(id = message_id).first() or None

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        if message == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat_message == None and message != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
        
        user_chat_message.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)    