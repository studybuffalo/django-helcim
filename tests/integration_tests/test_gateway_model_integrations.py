"""Integration tests between Gateway and Model modules."""
from datetime import datetime
from unittest.mock import patch

import pytest

from helcim import exceptions as helcim_exceptions, gateway, models


pytestmark = pytest.mark.django_db # pylint: disable=invalid-name

def test__save_transaction__saves_to_model():
    """Confirms that models are created as expected."""
    count = models.HelcimTransaction.objects.all().count()

    # Create request and mock response
    base = gateway.BaseRequest()
    base.response = {
        'transaction_success': True,
        'transaction_date': datetime(2018, 1, 1).date(),
        'transaction_time': datetime(2018, 1, 1, 1, 2, 3).time(),
    }

    # Redact response (as expected in usual handling)
    base.redact_data()

    # Save transaction and confirm transaction was created
    base.save_transaction('s')

    assert count + 1 == models.HelcimTransaction.objects.all().count()

def test__save_transaction__handles_unredacted_data():
    """Confirms that method still works when data has not yet been redacted."""
    count = models.HelcimTransaction.objects.all().count()

    # Create request and mock response
    base = gateway.BaseRequest()
    base.response = {
        'transaction_success': True,
        'transaction_date': datetime(2018, 1, 1).date(),
        'transaction_time': datetime(2018, 1, 1, 1, 2, 3).time(),
    }
    # Confirm that redacted response is Falsy
    base.redacted_response = {}

    # Save transaction and confirm handling as normal
    base.save_transaction('s')

    assert count + 1 == models.HelcimTransaction.objects.all().count()

def test__save_transaction__missing_required_field_handling():
    """Confirms proper error returns when field missing."""
    base = gateway.BaseRequest()
    base.response = {}

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

def test__save_transaction__invalid_data_type_handling():
    """Confirms error returned when invalide field type provided."""
    base = gateway.BaseRequest()
    base.response = {
        'transaction_success': True,
        'transaction_date': datetime(2018, 1, 1).date(),
        'transaction_time': datetime(2018, 1, 1, 1, 2, 3).time(),
        'transaction_id': 'a',
    }

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

@patch.dict('helcim.gateway.SETTINGS', {'enable_token_vault': True})
def test__save_token__saves_to_model(user):
    """Confirm models are created as expected."""
    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    base.save_token_to_vault()

    assert count + 1 == models.HelcimToken.objects.all().count()

@patch.dict('helcim.gateway.SETTINGS', {'enable_token_vault': True})
def test__save_token__saves_to_model_with_user(user):
    """Confirms model created with expected user reference."""
    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    base.save_token_to_vault()

    assert count + 1 == models.HelcimToken.objects.all().count()

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'allow_anonymous': False},
)
def test__save_token__handles_duplicate_token_with_associate(user):
    """Confirms handling with duplicate token and associated user."""
    first_instance = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        customer_code='CST1000',
        django_user=user,
    )

    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    second_instance = base.save_token_to_vault()

    assert count == models.HelcimToken.objects.all().count()
    assert first_instance == second_instance

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'allow_anonymous': True},
)
def test__save_token__handles_duplicate_token_without_associate():
    """Confirms handling with duplicate token and no associated user."""
    first_instance = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        customer_code='CST1000',
        django_user=None,
    )

    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=None)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    second_instance = base.save_token_to_vault()

    assert count == models.HelcimToken.objects.all().count()
    assert first_instance == second_instance
