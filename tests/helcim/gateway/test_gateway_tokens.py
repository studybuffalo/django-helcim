"""Tests for the token functions in the Gateway module."""
from unittest.mock import patch

import pytest

from helcim import gateway, exceptions as helcim_exceptions, models


pytestmark = pytest.mark.django_db # pylint: disable=invalid-name

class MockHelcimToken():
    """Mock of the HelcimToken model."""
    # pylint: disable=redefined-builtin, unused-argument
    def __init__(self, id=None, django_user=None, customer_code=None):
        self.token = 'abcdefghijklmnopqrstuvw'
        self.token_f4l4 = '11114444'
        self.django_user = django_user
        self.customer_code = customer_code

class MockHelcimTokenDoesNotExist():
    """Mocks the HelcimToken DoesNotExist exception."""
    # pylint: disable=redefined-builtin, unused-argument
    def __init__(self, id=None, customer_code=None, django_user=None):
        raise models.HelcimToken.DoesNotExist

class MockHelcimTokenFilter():
    """Mock of the HelcimToken filter function."""
    def __init__(self, django_user=None, customer_code=None):
        self.django_user = django_user
        self.customer_code = customer_code

def test_retrieve_token_details_customer_code_only():
    """Tests that retrieval with customer code only works."""
    token = models.HelcimToken.objects.create(
        token='a', token_f4l4='11114444', customer_code='1'
    )
    token_details = gateway.retrieve_token_details(token.id, customer_code='1')

    assert token_details['token'] == 'a'
    assert token_details['token_f4l4'] == '11114444'
    assert token_details['django_user'] is None
    assert token_details['customer_code'] == '1'

def test_retrieve_token_details_with_user(django_user_model):
    """Tests that retrieval with customer code and user works."""
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    token = models.HelcimToken.objects.create(
        token='a', token_f4l4='11114444', django_user=user, customer_code='1'
    )
    token_details = gateway.retrieve_token_details(
        token.id, django_user=user, customer_code='1'
    )

    assert token_details['token'] == 'a'
    assert token_details['token_f4l4'] == '11114444'
    assert token_details['django_user'] == user
    assert token_details['customer_code'] == '1'

def test_retrieve_token_details_missing_customer_code():
    """Tests that retrieval without customer code causes error."""
    token = models.HelcimToken.objects.create(
        token='a', token_f4l4='11114444', customer_code='1'
    )

    try:
        gateway.retrieve_token_details(token.id)
    except helcim_exceptions.ProcessingError as error:
        assert str(error) == (
            'Unable to retrieve token details for specified customer.'
        )
    else:
        assert False

def test_retrieve_token_details_missing_user(django_user_model):
    """Tests that retrieval without user causes error (when added)."""
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    token = models.HelcimToken.objects.create(
        token='a', token_f4l4='11114444', django_user=user, customer_code='1'
    )

    try:
        gateway.retrieve_token_details(token.id, customer_code='1')
    except helcim_exceptions.ProcessingError as error:
        assert str(error) == (
            'Unable to retrieve token details for specified customer.'
        )
    else:
        assert False

@patch(
    'helcim.bridge_oscar.gateway.models.HelcimToken.objects.get',
    MockHelcimTokenDoesNotExist
)
def test_retrieve_token_details_invalid():
    """Tests that dictionary is properly built."""
    try:
        gateway.retrieve_token_details('1', '2')
    except helcim_exceptions.ProcessingError:
        assert True
    else:
        assert False

@patch(
    'helcim.gateway.models.HelcimToken.objects.filter',
    MockHelcimTokenFilter
)
@patch.dict('helcim.gateway.SETTINGS', {'associate_user': True})
def test_retrieve_saved_tokens_by_django_user():
    """Tests that tokens can be retrieved for a Django user."""
    tokens = gateway.retrieve_saved_tokens(django_user='1')

    assert tokens.django_user == '1'
    assert tokens.customer_code is None

@patch(
    'helcim.gateway.models.HelcimToken.objects.filter',
    MockHelcimTokenFilter
)
@patch.dict('helcim.gateway.SETTINGS', {'associate_user': False})
def test_retrieve_saved_tokens_by_customer_code():
    """Tests that tokens can be retrieved for a customer code."""
    tokens = gateway.retrieve_saved_tokens(customer_code='1')

    assert tokens.django_user is None
    assert tokens.customer_code == '1'
