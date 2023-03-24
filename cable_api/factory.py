import factory
from factory.faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    user_name = factory.Sequence(lambda n: 'test{}'.format(n))
    email_address = factory.Sequence(lambda n: 'test{}@test.com'.format(n))
    password = factory.LazyFunction(lambda: make_password('pi3.1415'))
    profile_image = factory.django.ImageField(width=60, height=60)