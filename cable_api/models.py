from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    """
    A Class that defines methodes to manage the custom user model.
    """

    def create_user(self, user_name, email_address, password):
        """
        A method responsible for creating a new user and saving them to the database.
        """

        user = self.model(
            email_address = self.normalize_email(email_address),
            user_name = user_name,
            password = password
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, user_name, email_address, password):
        """
        A method responsible for creating a new user with admin privilages. 
        """

        user = self.model(
            email_address = self.normalize_email(email_address),
            user_name = user_name,
            password = password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using = self._db)
        
        return user
    
class User(AbstractBaseUser):
    """
    A Class that defines:
    - The fields of the custom user model.
    - The manager for the custom user model.
    - The username field.
    - The required fields.
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

    objects = UserManager()

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['user_name', 'password']