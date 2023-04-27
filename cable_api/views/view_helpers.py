from rest_framework.exceptions import NotFound

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