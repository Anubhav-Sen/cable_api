import factory
from factory.faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from cable_api.models import Chat, Participant, Message

class UserFactory(factory.django.DjangoModelFactory):
    """
    A class to define the user factory and the contents of the objects generated by it.
    """
    class Meta:
        model = get_user_model()

    user_name = factory.Sequence(lambda n: 'test{}'.format(n))
    email_address = factory.Sequence(lambda n: 'test{}@test.com'.format(n))
    password = factory.LazyFunction(lambda: make_password('testpassword'))
    profile_image = factory.django.ImageField(width=60, height=60)

class ChatFactory(factory.django.DjangoModelFactory):
    """
    A class to define the chat factory and the contents of the objects generated by it.
    """
    class Meta:
        model = Chat

    display_name = factory.Sequence(lambda n: 'chat_{}'.format(n))

class ParticipantFactory(factory.django.DjangoModelFactory):
    """
    A class to define the participant factory and the contents of the objects generated by it.
    """
    class Meta:
        model = Participant

    model_user = factory.SubFactory(UserFactory)
    chat = factory.SubFactory(ChatFactory)

class MessageFactory(factory.django.DjangoModelFactory):
    """
    A class to define the message factory and the contents of the objects generated by it.
    """
    class Meta:
        model = Message

    content = Faker('text', max_nb_chars = 200)
    chat = factory.SubFactory(ChatFactory)
    sender = factory.SubFactory(UserFactory)
    