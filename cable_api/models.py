from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class User(AbstractBaseUser):
    """
    A Class that defines the fields of the custom user model.
    """

    user_name = models.CharField(max_length=50)
    email_address = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['user_name', 'email_address', 'password']