from rest_framework.exceptions import APIException

class Unauthorized(APIException):
    """
    A class that defines the unauthorized exception.
    """
    status_code = 401
    default_detail = None
    default_code = None