from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.models import Chat, Participant
from cable_api.serializers import ChatSerializer, EmailSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  
def chats_view(request):
    """
    A function that defines the "api/chats/" endpoint.
    """
    if request.method == 'GET':

        chats = Chat.objects.filter(participants__model_user = request.user).all() or None

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

        chat_user = get_user_model().objects.filter(email_address = email_serializer.validated_data['email_address']).first() or None

        existing_chat = Chat.objects.filter(participants__model_user = chat_user).filter(participants__model_user = request.user).first() or None

        if email_serializer.validated_data['email_address'] == request.user.email_address:

            response_dict = {'detail': "Email provided cannot be the same as the authenticated user's."}

            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        
        if chat_user == None:
            
            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

        if existing_chat != None:

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
    A function that defines the "api/chats/chat_id/" endpoint.
    """
    if request.method == 'GET':
        
        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
           
        chat_serializer = ChatSerializer(user_chat)

        response_dict = {'chat': chat_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':

        chat_serializer = ChatSerializer(data=request.data)  
        chat_serializer.is_valid(raise_exception=True)
        
        chat = Chat.objects.filter(id = chat_id).first() or None

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first() or None

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)
            
        for key, value in chat_serializer.validated_data.copy().items():
            
            if value == None:

                chat_serializer.validated_data.pop(key)
                    
        Chat.objects.filter(id = chat_id).update(**chat_serializer.validated_data)
        
        updated_chat = Chat.objects.get(id = chat_id)       

        chat_serializer = ChatSerializer(updated_chat)    

        response_dict = {'updated_chat': chat_serializer.data} 
    
        return Response(response_dict, status=status.HTTP_200_OK)   
    
    elif request.method == 'DELETE':

        chat = Chat.objects.filter(id = chat_id).first()

        user_chat = Chat.objects.filter(participants__model_user = request.user).filter(id = chat_id).first()

        if chat == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        if user_chat == None and chat != None:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

            return Response(response_dict, status=status.HTTP_401_UNAUTHORIZED)   
        
        user_chat.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)