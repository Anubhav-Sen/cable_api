from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from cable_api.serializers import UserSerializer, UserUpdateSerializer
from cable_api.views.view_helpers import *

@api_view(['GET', 'POST'])
def users_view(request):
    """
    A function that defines the "api/users/" endpoint.
    """
    if request.method == 'GET':

        users = get_object_list_or_404(get_user_model())

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
    A function that defines the methods of the "api/users/user_id/" endpoint.
    """    
    if request.method == 'GET':

        user = get_object_or_404(get_user_model(), id = user_id)
        
        user_serializer = UserSerializer(user)

        response_dict = {'user': user_serializer.data}

        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':

        user_update_serializer = UserUpdateSerializer(data=request.data)  
        user_update_serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(get_user_model(), id = user_id)
        
        check_user_object_perms(user, request.user)
             
        update_data = clean_serializer_data(user_update_serializer.validated_data)
                         
        get_user_model().objects.filter(id = user_id).update(**update_data)

        updated_user = get_user_model().objects.get(id = user_id)       

        user_serializer = UserSerializer(updated_user)    

        response_dict = {'updated_user': user_serializer.data} 
    
        return Response(response_dict, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':

        user = get_object_or_404(get_user_model(), id = user_id)

        check_user_object_perms(user, request.user)
        
        user.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)