from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from cable_api.serializers import UserSerializer, UserUpdateSerializer

def get_object_list_or_404(model, **filters):
    """
    A function that:
    - Query's a model for a list of objects with the given filter arguments.
    - Returns the list of objects if they exist and raises an exception if they dont.
    """ 
    obj_list = model.objects.filter(**filters).all()
        
    if not obj_list: 

        raise NotFound('These objects do not exist.')
    
    return obj_list

def get_object_or_404(model, **filters):
    """
    A function that:
    - Query's a model for a object with the given filter arguments.
    - Returns the object if it exists and raises an exception if is doesn't.
    """
    obj = model.objects.filter(**filters).first()
        
    if not obj: 

        raise NotFound('This object does not exist.')
    
    return obj
        
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
        
        user = get_user_model().objects.filter(id = user_id).first() or None

        if user == None:
 
            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        elif request.user.id != user_id:

            response_dict = {'detail': 'Unauthorized to use this method on this endpoint or object.'}

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

        user = get_user_model().objects.filter(id = user_id).first() or None

        if user == None:

            response_dict = {'detail': 'This object does not exist.'}

            return Response(response_dict, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()

        response_dict = {'detail': 'This object has been deleted.'}

        return Response(response_dict, status=status.HTTP_200_OK)