"""Tests for the token functions in the Gateway module."""
from unittest.mock import patch

from helcim import gateway, exceptions as helcim_exceptions, models


class MockHelcimToken():
    """Mock of the HelcimToken model."""
    # pylint: disable=redefined-builtin, unused-argument
    def __init__(self, id=None, django_user=None):
        self.token = 'abcdefghijklmnopqrstuvw'
        self.token_f4l4 = '11114444'
        self.customer_code = 'CST0001'

class MockHelcimTokenDoesNotExist():
    """Mocks the HelcimToken DoesNotExist exception."""
    # pylint: disable=redefined-builtin, unused-argument
    def __init__(self, id=None, django_user=None):
        raise models.HelcimToken.DoesNotExist

class MockHelcimTokenFilter():
    """Mock of the HelcimToken filter function."""
    def __init__(self, django_user=None, customer_code=None):
        self.django_user = django_user
        self.customer_code = customer_code

@patch(
    'helcim.bridge_oscar.gateway.models.HelcimToken.objects.get',
    MockHelcimToken
)
def test_retrieve_token_details_valid():
    """Tests that dictionary is properly built."""
    token_details = gateway.retrieve_token_details('1', '2')

    assert token_details['token'] == 'abcdefghijklmnopqrstuvw'
    assert token_details['token_f4l4'] == '11114444'
    assert token_details['customer_code'] == 'CST0001'

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
@patch.dict('helcim.gateway.SETTINGS', {'token_vault_identifier': 'django'})
def test_retrieve_saved_tokens_by_django_user():
    """Tests that tokens can be retrieved for a Django user."""
    tokens = gateway.retrieve_saved_tokens('1')

    assert tokens.django_user == '1'
    assert tokens.customer_code is None

@patch(
    'helcim.gateway.models.HelcimToken.objects.filter',
    MockHelcimTokenFilter
)
@patch.dict('helcim.gateway.SETTINGS', {'token_vault_identifier': 'helcim'})
def test_retrieve_saved_tokens_by_customer_code():
    """Tests that tokens can be retrieved for a customer code."""
    tokens = gateway.retrieve_saved_tokens('1')

    assert tokens.django_user is None
    assert tokens.customer_code == '1'
