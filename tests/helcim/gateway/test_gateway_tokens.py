"""Tests for the token functions in the Gateway module."""
from unittest.mock import patch

from helcim import bridge_oscar, exceptions as helcim_exceptions, models


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

@patch(
    'helcim.bridge_oscar.gateway.models.HelcimToken.objects.get',
    MockHelcimToken
)
def test_retrieve_token_details_valid():
    """Tests that dictionary is properly built."""
    token_details = bridge_oscar.retrieve_token_details('1', '2')

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
        bridge_oscar.retrieve_token_details('1', '2')
    except helcim_exceptions.ProcessingError:
        assert True
    else:
        assert False

# TODO: Add tests for retrieve_saved_tokens
