"""Integration tests between Gateway and Model modules."""
# pylint: disable=protected-access
from datetime import datetime
from unittest.mock import patch

import pytest

from helcim import exceptions as helcim_exceptions, gateway, models


pytestmark = pytest.mark.django_db # pylint: disable=invalid-name

def test__base_request__save_transaction__saves_to_model():
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

def test__base_request__save_transaction__handles_unredacted_data():
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

def test__base_request__save_transaction__missing_required_field_handling():
    """Confirms proper error returns when field missing."""
    base = gateway.BaseRequest()
    base.response = {}

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

def test__base_request__save_transaction__invalid_data_type_handling():
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
def test__base_card_transaction__save_token__saves_to_model(user):
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
def test__base_card_transaction__save_token__saves_to_model_with_user(user):
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
def test__base_card_transaction__save_token___duplicate_with_associate(user):
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
def test__base_card_transaction__save_token__duplicate_without_associate():
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

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'allow_anonymous': True},
)
def test__helcim_js_response__record_response():
    """Confirms expected models created with _record_response."""
    # Get initial model counts
    trans_count = models.HelcimTransaction.objects.all().count()
    token_count = models.HelcimToken.objects.all().count()

    # Generate response
    raw_response = {
        'response': '1',
        'responseMessage': 'APPROVED',
        'noticeMessage': 'New Card Stored',
        'cardNumber': '1111 **** **** 9999',
        'cardExpiry': '0150',
        'cardToken': '1234567890abcdefghijkl',
        'customerCode': 'CST1000',
        'date': '2020-01-01',
        'time': '01:02:03',
    }
    response = gateway.HelcimJSResponse(raw_response, save_token=True)

    # Validate data to prepare for recording
    assert response.is_valid()

    # Record purchase
    transaction, token = response._record_response('s')

    # Confirm model instance counts increased
    assert models.HelcimTransaction.objects.all().count() == trans_count + 1
    assert models.HelcimToken.objects.all().count() == token_count + 1

    # Confirm some expected details
    transaction.customer_code = 'CST1000'
    transaction.transacton_type = 's'
    token.customer_code = 'CST1000'
    token.token = '1234567890abcdefghijkl'

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'allow_anonymous': True},
)
def test__helcim_js_response__record_purchase():
    """Confirms expected models created with record_purchase."""
    # Get initial model counts
    trans_count = models.HelcimTransaction.objects.all().count()
    token_count = models.HelcimToken.objects.all().count()

    # Generate response
    raw_response = {
        'response': '1',
        'responseMessage': 'APPROVED',
        'noticeMessage': 'New Card Stored',
        'cardNumber': '1111 **** **** 9999',
        'cardExpiry': '0150',
        'cardToken': '1234567890abcdefghijkl',
        'customerCode': 'CST1000',
        'date': '2020-01-01',
        'time': '01:02:03',
    }
    response = gateway.HelcimJSResponse(raw_response, save_token=True)

    # Validate data to prepare for recording
    assert response.is_valid()

    # Record purchase
    transaction, token = response.record_purchase()

    # Confirm model instance counts increased
    assert models.HelcimTransaction.objects.all().count() == trans_count + 1
    assert models.HelcimToken.objects.all().count() == token_count + 1

    # Confirm some expected details
    transaction.customer_code = 'CST1000'
    transaction.transacton_type = 's'
    token.customer_code = 'CST1000'
    token.token = '1234567890abcdefghijkl'

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'allow_anonymous': True},
)
def test__helcim_js_response__record_preauthorization():
    """Confirms expected models created with record_preauthorization."""
    # Get initial model counts
    trans_count = models.HelcimTransaction.objects.all().count()
    token_count = models.HelcimToken.objects.all().count()

    # Generate response
    raw_response = {
        'response': '1',
        'responseMessage': 'APPROVED',
        'noticeMessage': 'New Card Stored',
        'cardNumber': '1111 **** **** 9999',
        'cardExpiry': '0150',
        'cardToken': '1234567890abcdefghijkl',
        'customerCode': 'CST1000',
        'date': '2020-01-01',
        'time': '01:02:03',
    }
    response = gateway.HelcimJSResponse(raw_response, save_token=True)

    # Validate data to prepare for recording
    assert response.is_valid()

    # Record purchase
    transaction, token = response.record_preauthorization()

    # Confirm model instance counts increased
    assert models.HelcimTransaction.objects.all().count() == trans_count + 1
    assert models.HelcimToken.objects.all().count() == token_count + 1

    # Confirm some expected details
    transaction.customer_code = 'CST1000'
    transaction.transacton_type = 'p'
    token.customer_code = 'CST1000'
    token.token = '1234567890abcdefghijkl'

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'allow_anonymous': True},
)
def test__helcim_js_response__record_verification():
    """Confirms expected models created with record_verification."""
    # Get initial model counts
    trans_count = models.HelcimTransaction.objects.all().count()
    token_count = models.HelcimToken.objects.all().count()

    # Generate response
    raw_response = {
        'response': '1',
        'responseMessage': 'APPROVED',
        'noticeMessage': 'New Card Stored',
        'cardNumber': '1111 **** **** 9999',
        'cardExpiry': '0150',
        'cardToken': '1234567890abcdefghijkl',
        'customerCode': 'CST1000',
        'date': '2020-01-01',
        'time': '01:02:03',
    }
    response = gateway.HelcimJSResponse(raw_response, save_token=True)

    # Validate data to prepare for recording
    assert response.is_valid()

    # Record purchase
    transaction, token = response.record_verification()

    # Confirm model instance counts increased
    assert models.HelcimTransaction.objects.all().count() == trans_count + 1
    assert models.HelcimToken.objects.all().count() == token_count + 1

    # Confirm some expected details
    transaction.customer_code = 'CST1000'
    transaction.transacton_type = 'v'
    token.customer_code = 'CST1000'
    token.token = '1234567890abcdefghijkl'
