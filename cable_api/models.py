from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from cable_api.storage import OverwriteStorage

def profile_image_path(instance, filename):
    """
    A function responsible for generating a file path to store the users profile image.
    """
    extension = filename.split('.')[-1]

    filename = f'profile_image.{extension}'

    path = f'users/{instance.email_address}/profile_image/{filename}'

    return path

class UserManager(BaseUserManager):
    """
    A Class that defines methodes to manage the custom user model.
    """
    def create_user(self, user_name, email_address, password, **kwargs):
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
        A method responsible for creating a new user with administrative privilages set to true. 
        """
        user = self.model(
            email_address = self.normalize_email(email_address),
            user_name = user_name,
            password = password
        )
 
        user.set_password(password)
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
    - The __str__ method for the user model.
    - Methods to handel permissions.
    """
    user_name = models.CharField(max_length=50)
    email_address = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to=profile_image_path, storage=OverwriteStorage(), null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['user_name', 'password']

    def __str__(self):
        """
        Method that returns the email address of the user to represent the user object in string format.
        """
        return self.email_address

    def has_perm(self, perm, obj=None):
        """
        Method that checks if user has a specific permission. In this case user always has permissions.
        """
        return True
    
    def has_module_perms(self, app):
        """
        Method that checks if user has permissions to view a certain app. In this case a user can always view all apps.
        """
        return True
    
class Chat(models.Model):
    """
    A class that defines:
    - The fields of the chat model.
    - The __str__ method for the chat model.
    """
    display_name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Method that returns the chat id to represent the chat object in string format.
        """

        return f"chat_{self.id}"
    
class Participant(models.Model):
    """
    A class that defines:
    - The fields of the participant model.
    - The __str__ method for the chat model.
    """
    model_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='participants')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['chat', 'model_user'], name='unique_chat_and_participant_combination')
        ]

    def __str__(self):
        """
        Method that returns the participant id to represent the participant object in string format.
        """
        return f'participant_{self.id}'
    
class Message(models.Model):
    """
     A class that defines:
    - The fields of the Message model.
    - The __str__ method for the chat model.
    """
    content = models.TextField();
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        This method defines the string to be returned for the model object.
        """
        return f'message_{self.id}'