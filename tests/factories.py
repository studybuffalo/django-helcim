"""Factories for django-helcim tests."""
# pylint: disable=unnecessary-lambda
import factory

from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    """Creates a user model instance."""
    username = factory.Sequence(lambda n: 'User {}'.format(n))
    email = factory.Sequence(lambda n: 'user_{}@email.com'.format(n))
    password = 'password'

    class Meta:
        model = get_user_model()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override _create to use the create_user method."""
        manager = cls._get_manager(model_class)

        return manager.create_user(*args, **kwargs)
