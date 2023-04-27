from rest_framework.exceptions import NotFound, ParseError
from cable_api.models import Chat
from cable_api.exceptions import Unauthorized

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

def check_user_object_perms(obj, auth_user):
    """
    A function that compares the user object passed to it to the authenticated user and raises an exception if they are not the same.
    """
    if obj != auth_user:

        raise Unauthorized('Unauthorized to use this method on this endpoint or object.')
    
def check_object_perms(obj, **user_filter):
    """
    A function that:
    - Query's the model of the object passed to it with its object id as a filter.
    - It applies an additional filter with a user model object as its value to check if the object belongs to the user.
    - If the object dosen't exist a unauthorized exception is raised.
    """
    model = type(obj)

    obj_filtered_by_user = model.objects.filter(id = obj.id).filter(**user_filter).first()

    if not obj_filtered_by_user:

        raise Unauthorized('Unauthorized to use this method on this endpoint or object.')
    
def clean_serializer_data(data):
    """
    A function that:
    - Creates a copy of a serializer's validated data dictionary.
    - Pops all keys that have null values.
    - Returns the cleaned data.
    """

    data = data.copy()

    for key, value in data.items():
    
        if value == None:

            data.pop(key)

    return data

def check_chat_exists(chat_user, auth_user):
    """
    A function that query's the chat model with the chat user and auth user objects to check if a chat with those users already exists.
    """
    existing_chat = Chat.objects.filter(participants__model_user = chat_user).filter(participants__model_user = auth_user).first()

    if existing_chat:

        raise ParseError('This object already exists.')

def compare_email(email, auth_user_email):
    """
    A function that compares the email addres passed to it to the email addres of the authenticated user.
    """
    if email == auth_user_email:

        raise ParseError("Email provided cannot be the same as the authenticated user's.")