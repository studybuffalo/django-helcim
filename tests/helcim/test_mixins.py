"""Tests for django-helcim mixins."""
# pylint: disable=too-few-public-methods, protected-access, line-too-long
from datetime import date, datetime
from unittest.mock import patch

import pytest

from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.utils.safestring import SafeString

from helcim import exceptions as helcim_exceptions
from helcim.mixins import ResponseMixin, HelcimJSMixin


pytestmark = pytest.mark.django_db # pylint: disable=invalid-name

class MockDjangoModel():
    """Mock of basic Django model."""
    def __init__(self, **kwargs):
        self.data = kwargs

class MockView():
    """Mocked Django view for mixin testing."""
    def __init__(self):
        pass

    def get_context_data(self, **kwargs):
        """Mimics normal method for testing."""
        context = {**kwargs}

        return context

class MockMixinView(HelcimJSMixin, MockView):
    """Mocked view with mixin."""
    pass

class ResponseMixinModel(ResponseMixin):
    """Generic object to inherit TransactionMixin methods.

        Allows the declaration of required object attributes to test
        mixin methods.
    """
    def __init__(self, **kwargs):
        self.django_user = kwargs.get('django_user', None)
        self.redacted_response = kwargs.get('redacted_response', None)
        self.response = kwargs.get('response', None)
        self.save_token = kwargs.get('save_token', False)

def mock_get_or_create_created(**kwargs):
    """Mock of the get_or_create method."""
    return (MockDjangoModel(**kwargs), True)

def mock_integrity_error(**kwargs): # pylint: disable=unused-argument
    """Mocks raising an IntegrityError."""
    raise IntegrityError

def mock_value_error(**kwargs): # pylint: disable=unused-argument
    """Mocks raising an ValueError."""
    raise ValueError


def test__response__redact_field__only_redacts_specified_details():
    """Tests that non-specified fields are not redacted."""
    redacted_response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_field('cardNumber', 'cc_number')

    assert len(mixin.redacted_response) == 3
    assert mixin.redacted_response['raw_request'] == 'cardHolderName=a'
    assert mixin.redacted_response['raw_response'] == (
        '<cardHolderName>a</cardHolderName>'
    )
    assert mixin.redacted_response['cc_name'] == 'a'

def test__response__identify_redact_fields__defaults():
    """Tests for expected output from method."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    # Length is tested to warn of any changes to fields
    assert len(fields) == 8
    assert fields['name']['redact'] is True
    assert fields['number']['redact'] is True
    assert fields['expiry']['redact'] is True
    assert fields['cvv']['redact'] is True
    assert fields['type']['redact'] is True
    assert fields['token']['redact'] is False
    assert fields['mag']['redact'] is True
    assert fields['mag_enc']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_all': True})
def test__response__identify_redact_fields__redact_all_true():
    """Tests that redact_all = True applies to all fields."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['name']['redact'] is True
    assert fields['number']['redact'] is True
    assert fields['expiry']['redact'] is True
    assert fields['cvv']['redact'] is True
    assert fields['type']['redact'] is True
    assert fields['token']['redact'] is True
    assert fields['mag']['redact'] is True
    assert fields['mag_enc']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_all': False})
def test__response__identify_redact_fields__redact_all_false():
    """Tests that redact_all = False applies to all fields."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['name']['redact'] is False
    assert fields['number']['redact'] is False
    assert fields['expiry']['redact'] is False
    assert fields['cvv']['redact'] is False
    assert fields['type']['redact'] is False
    assert fields['token']['redact'] is False
    assert fields['mag']['redact'] is False
    assert fields['mag_enc']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_name': True})
def test__response__identify_redact_fields__redact_name_true():
    """Tests that redact_cc_name = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['name']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_name': False})
def test__response__identify_redact_fields__redact_name_false():
    """Tests that redact_cc_name = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['name']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_number': True})
def test__response__identify_redact_fields__redact_number_true():
    """Tests that redact_cc_number = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['number']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_number': False})
def test__response__identify_redact_fields__redact_number_false():
    """Tests that redact_cc_number = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['number']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_expiry': True})
def test__response__identify_redact_fields__redact_expiry_true():
    """Tests that redact_cc_expiry = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['expiry']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_expiry': False})
def test__response__identify_redact_fields__redact_expiry_false():
    """Tests that redact_cc_expiry = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['expiry']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_cvv': True})
def test__response__identify_redact_fields__redact_cvv_true():
    """Tests that redact_cc_cvv = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['cvv']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_cvv': False})
def test__response__identify_redact_fields__redact_cvv_false():
    """Tests that redact_cc_cvv = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['cvv']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_type': True})
def test__response__identify_redact_fields__redact_type_true():
    """Tests that redact_cc_type = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['type']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_type': False})
def test__response__identify_redact_fields__redact_type_false():
    """Tests that redact_cc_type = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['type']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_token': True})
def test__response__identify_redact_fields__redact_token_true():
    """Tests that redact_token = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['token']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_token': False})
def test__response__identify_redact_fields__redact_token_false():
    """Tests that redact_token = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['token']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic': True})
def test__response__identify_redact_fields__redact_mag_true():
    """Tests that cc_magnetic = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['mag']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic': False})
def test__response__identify_redact_fields__redact_mag_false():
    """Tests that cc_magnetic = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['mag']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic_encrypted': True})
def test__response__identify_redact_fields__redact_mag_enc_true():
    """Tests that cc_magnetic_encrypted = True applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['mag_enc']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic_encrypted': False})
def test__response__identify_redact_fields__redact_mag_enc_false():
    """Tests that cc_magnetic_encrypted = False applies to expected field."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['mag_enc']['redact'] is False

@patch.dict(
    'helcim.gateway.SETTINGS',
    {
        'redact_all': True,
        'redact_cc_name': False,
        'redact_cc_number': False,
        'redact_cc_expiry': False,
        'redact_cc_cvv': False,
        'redact_cc_type': False,
        'redact_token': False,
        'redact_cc_magnetic': False,
        'redact_cc_magnetic_encrypted': True,
    }
)
def test__response__identify_redact_fields__redact_all_true_overrides():
    """Confirms that redact_all = True overrides all other redact settings."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['name']['redact'] is True
    assert fields['number']['redact'] is True
    assert fields['expiry']['redact'] is True
    assert fields['cvv']['redact'] is True
    assert fields['type']['redact'] is True
    assert fields['token']['redact'] is True
    assert fields['mag']['redact'] is True
    assert fields['mag_enc']['redact'] is True

@patch.dict(
    'helcim.gateway.SETTINGS',
    {
        'redact_all': False,
        'redact_cc_name': True,
        'redact_cc_number': True,
        'redact_cc_expiry': True,
        'redact_cc_cvv': True,
        'redact_cc_type': True,
        'redact_token': True,
        'redact_cc_magnetic': True,
        'redact_cc_magnetic_encrypted': True,
    }
)
def test__response__identify_redact_fields__redact_all_false_overrides():
    """Confirms that redact_all = False overrides all other redact settings."""
    mixin = ResponseMixinModel()
    fields = mixin._identify_redact_fields()

    assert fields['name']['redact'] is False
    assert fields['number']['redact'] is False
    assert fields['expiry']['redact'] is False
    assert fields['cvv']['redact'] is False
    assert fields['type']['redact'] is False
    assert fields['token']['redact'] is False
    assert fields['mag']['redact'] is False
    assert fields['mag_enc']['redact'] is False

def test__response__convert_expiry_to_date():
    """Confirms CC expiry is converted to expected Python datetime."""
    mixin = ResponseMixinModel()
    expiry = mixin._convert_expiry_to_date('0118')

    assert expiry == datetime(2018, 1, 31).date()

@patch.dict('helcim.mixins.SETTINGS', {'enable_token_vault': True})
def test__response__determine_save_token_status__enabled_user_yes():
    """Confirms save token status when vault enabled & user = True."""
    mixin = ResponseMixinModel()
    status = mixin._determine_save_token_status(True)

    assert status is True

@patch.dict('helcim.mixins.SETTINGS', {'enable_token_vault': True})
def test__response__determine_save_token_status__enabled_user_no():
    """Confirms save token status when vault enabled & user = False."""
    mixin = ResponseMixinModel()
    status = mixin._determine_save_token_status(False)

    assert status is False

@patch.dict('helcim.mixins.SETTINGS', {'enable_token_vault': False})
def test__response__determine_save_token_status__disabled_user_yes():
    """Confirms save token status when vault disabled & user = True."""
    mixin = ResponseMixinModel()
    status = mixin._determine_save_token_status(True)

    assert status is False

@patch.dict('helcim.mixins.SETTINGS', {'enable_token_vault': False})
def test__response__determine_save_token_status__disabled_user_no():
    """Confirms save token status when vault disabled & user = False."""
    mixin = ResponseMixinModel()
    status = mixin._determine_save_token_status(False)

    assert status is False

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': True})
def test__response__determine_user_reference__allow_anonymous_with_user(user):
    """Tests that method returns proper user reference."""
    mixin = ResponseMixinModel(django_user=user)
    returned_user = mixin._determine_user_reference()

    assert returned_user == user

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': True})
def test__response__determine_user_reference__allow_anonymous_with_anonymous():
    """Tests that method returns None as this is an anonymous user."""
    user = AnonymousUser()
    mixin = ResponseMixinModel(django_user=user)
    returned_user = mixin._determine_user_reference()

    assert returned_user is None

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': True})
def test__response__determine_user_reference__allow_anonymous_with_none():
    """Tests that method None as no user provided."""
    mixin = ResponseMixinModel(django_user=None)
    returned_user = mixin._determine_user_reference()

    assert returned_user is None

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': False})
def test__response__determine_user_reference__no_anonymous_with_user(user):
    """Tests that user reference is returned as expected."""
    mixin = ResponseMixinModel(django_user=user)
    returned_user = mixin._determine_user_reference()

    assert returned_user == user

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': False})
def test__response__determine_user_reference_no_anonymous_with_none():
    """Tests that method returns error when user not provided."""
    mixin = ResponseMixinModel()

    try:
        mixin._determine_user_reference()
    except helcim_exceptions.ProcessingError as error:
        assert str(error) == 'Required Django user reference not provided.'
    else:
        assert False

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': False})
def test__response__determine_user_reference_no_anonymous_with_anonymous():
    """Tests that method returns error when user not provided."""
    user = AnonymousUser()
    mixin = ResponseMixinModel(django_user=user)

    try:
        mixin._determine_user_reference()
    except helcim_exceptions.ProcessingError as error:
        assert str(error) == 'Required Django user reference not provided.'
    else:
        assert False

def test__response__redact_api_data__account_id():
    """Tests that method redacts account ID."""
    redacted_response = {'raw_request': 'accountId=1'}
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_api_data()

    assert mixin.redacted_response['raw_request'] == 'accountId=REDACTED'

def test__response__redact_api_data__api_token():
    """Tests that method redacts API token."""
    redacted_response = {'raw_request': 'apiToken=1'}
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_api_data()

    assert mixin.redacted_response['raw_request'] == 'apiToken=REDACTED'

def test__response__redact_api_data__terminal_id():
    """Tests that method redacts terminal ID."""
    redacted_response = {'raw_request': 'terminalId=1'}
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_api_data()

    assert mixin.redacted_response['raw_request'] == 'terminalId=REDACTED'

def test__response__redact_api_data__all_fields():
    """Tests that method redacts all expected fields."""
    redacted_response = {
        'raw_request': 'accountId=1&apiToken=2&terminalId=3',
    }
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_api_data()

    assert mixin.redacted_response['raw_request'] == (
        'accountId=REDACTED&apiToken=REDACTED&terminalId=REDACTED'
    )

def test__response__redact_api_data__no_raw_request():
    """Tests that method handles no raw_request present."""
    redacted_response = {}
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_api_data()

    assert mixin.redacted_response['raw_request'] is None

def test__response__redact_field():
    """Tests that provided fields are redacted."""
    redacted_response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    mixin = ResponseMixinModel(redacted_response=redacted_response)

    mixin._redact_field('cardHolderName', 'cc_name')

    assert mixin.redacted_response['raw_request'] == 'cardHolderName=REDACTED'
    assert mixin.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName>'
    )
    assert mixin.redacted_response['cc_name'] is None

@patch.dict('helcim.mixins.SETTINGS', {'redact_cc_name': True})
def test__response__redact_data__cc_name():
    """Confirms redact_cc_name applies to all expected outputs."""
    response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    mixin = ResponseMixinModel(response=response)
    mixin.redact_data()

    assert mixin.redacted_response['raw_request'] == 'cardHolderName=REDACTED'
    assert mixin.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName>'
    )
    assert mixin.redacted_response['cc_name'] is None

@patch.dict('helcim.mixins.SETTINGS', {'redact_cc_number': True})
def test__response__redact_data__cc_number():
    """Confirms redact_cc_number applies to all expected outputs."""
    response = {
        'raw_request': 'cardNumber=a',
        'raw_response': '<cardNumber>a</cardNumber>',
        'cc_number': 'a',
    }
    mixin = ResponseMixinModel(response=response)
    mixin.redact_data()

    assert mixin.redacted_response['raw_request'] == 'cardNumber=REDACTED'
    assert mixin.redacted_response['raw_response'] == (
        '<cardNumber>REDACTED</cardNumber>'
    )
    assert mixin.redacted_response['cc_number'] is None

@patch.dict('helcim.mixins.SETTINGS', {'redact_cc_expiry': True})
def test__response__redact_data__cc_expiry():
    """Confirms redact_cc_expiry applies to all expected outputs."""
    response = {
        'raw_request': 'cardExpiry=a',
        'raw_response': '<cardExpiry>a</cardExpiry><expiryDate>b</expiryDate>',
        'cc_expiry': 'a',
    }
    mixin = ResponseMixinModel(response=response)
    mixin.redact_data()

    assert mixin.redacted_response['raw_request'] == 'cardExpiry=REDACTED'
    assert mixin.redacted_response['raw_response'] == (
        '<cardExpiry>REDACTED</cardExpiry><expiryDate>REDACTED</expiryDate>'
    )
    assert mixin.redacted_response['cc_expiry'] is None

@patch.dict('helcim.mixins.SETTINGS', {'redact_cc_type': True})
def test__response__redact_data__cc_type():
    """Confirms redact_cc_type applies to all expected outputs."""
    response = {
        'raw_request': 'cardType=a',
        'raw_response': '<cardType>a</cardType>',
        'cc_type': 'a',
    }
    mixin = ResponseMixinModel(response=response)
    mixin.redact_data()

    assert mixin.redacted_response['raw_request'] == 'cardType=REDACTED'
    assert mixin.redacted_response['raw_response'] == (
        '<cardType>REDACTED</cardType>'
    )
    assert mixin.redacted_response['cc_type'] is None

@patch.dict('helcim.mixins.SETTINGS', {'redact_token': True})
def test__response__redact_data__token():
    """Confirms redact_token applies to all expected outputs."""
    response = {
        'raw_request': 'cardToken=a&cardF4L4=11119999',
        'raw_response': (
            '<cardToken>a</cardToken><cardF4L4>11119999</cardF4L4>'
        ),
        'token': 'a',
        'token_f4l4': '11119999'
    }
    mixin = ResponseMixinModel(response=response)
    mixin.redact_data()

    assert mixin.redacted_response['raw_request'] == (
        'cardToken=REDACTED&cardF4L4=REDACTED'
    )
    assert mixin.redacted_response['raw_response'] == (
        '<cardToken>REDACTED</cardToken><cardF4L4>REDACTED</cardF4L4>'
    )
    assert mixin.redacted_response['token'] is None
    assert mixin.redacted_response['token_f4l4'] is None

@patch.dict('helcim.mixins.SETTINGS', {'redact_cc_name': True})
def test__response__redact_data__partial():
    """Confirms redactions only apply to expected fields."""
    response = {
        'raw_request': 'cardHolderName=a&cardToken=b',
        'raw_response': (
            '<cardHolderName>a</cardHolderName><cardToken>b</cardToken>'
        ),
        'cc_name': 'a',
        'token': 'b',
    }
    mixin = ResponseMixinModel(response=response)
    mixin.redact_data()

    assert mixin.redacted_response['raw_request'] == (
        'cardHolderName=REDACTED&cardToken=b'
    )
    assert mixin.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName><cardToken>b</cardToken>'
    )
    assert mixin.redacted_response['cc_name'] is None
    assert mixin.redacted_response['token'] == 'b'

def test__response__create_model_arguments__partial():
    """Confirms expected output when minimal details provided."""
    mixin = ResponseMixinModel(redacted_response={})
    arguments = mixin.create_model_arguments('z')

    assert len(arguments) == 22
    assert arguments['raw_request'] is None
    assert arguments['raw_response'] is None
    assert arguments['transaction_success'] is None
    assert arguments['response_message'] is None
    assert arguments['notice'] is None
    assert arguments['date_response'] is None
    assert arguments['transaction_id'] is None
    assert arguments['amount'] is None
    assert arguments['currency'] is None
    assert arguments['cc_name'] is None
    assert arguments['cc_number'] is None
    assert arguments['cc_expiry'] is None
    assert arguments['cc_type'] is None
    assert arguments['token'] is None
    assert arguments['avs_response'] is None
    assert arguments['cvv_response'] is None
    assert arguments['approval_code'] is None
    assert arguments['order_number'] is None
    assert arguments['customer_code'] is None
    assert arguments['transaction_type'] == 'z'
    assert arguments['django_user'] is None

def test__response__create_model_arguments__full():
    """Confirms expected output when all details provied."""
    redacted_response = {
        'raw_request': 'a',
        'raw_response': 'b',
        'transaction_success': 'c',
        'response_message': 'd',
        'notice': 'e',
        'transaction_date': datetime(2018, 1, 1).date(),
        'transaction_time': datetime(2018, 1, 1, 12, 0).time(),
        'transaction_id': 'f',
        'amount': 'g',
        'currency': 'h',
        'cc_name': 'i',
        'cc_number': 'j',
        'cc_expiry': '0620',
        'cc_type': 'k',
        'token': 'l',
        'token_f4l4': 'm',
        'avs_response': 'n',
        'cvv_response': 'o',
        'approval_code': 'p',
        'order_number': 'q',
        'customer_code': 'r',
    }
    mixin = ResponseMixinModel(redacted_response=redacted_response)
    arguments = mixin.create_model_arguments('z')

    assert len(arguments) == 22
    assert arguments['raw_request'] == 'a'
    assert arguments['raw_response'] == 'b'
    assert arguments['transaction_success'] == 'c'
    assert arguments['response_message'] == 'd'
    assert arguments['notice'] == 'e'
    assert arguments['date_response'] == datetime(2018, 1, 1, 12, 0)
    assert arguments['transaction_id'] == 'f'
    assert arguments['amount'] == 'g'
    assert arguments['currency'] == 'h'
    assert arguments['cc_name'] == 'i'
    assert arguments['cc_number'] == 'j'
    assert arguments['cc_expiry'] == datetime(2020, 6, 30).date()
    assert arguments['cc_type'] == 'k'
    assert arguments['token'] == 'l'
    assert arguments['token_f4l4'] == 'm'
    assert arguments['avs_response'] == 'n'
    assert arguments['cvv_response'] == 'o'
    assert arguments['approval_code'] == 'p'
    assert arguments['order_number'] == 'q'
    assert arguments['customer_code'] == 'r'
    assert arguments['transaction_type'] == 'z'
    assert arguments['django_user'] is None

def test__response__create_model_arguments__missing_time():
    """Confirms handling when transaction_time missing."""
    redacted_response = {
        'transaction_date': datetime(2018, 1, 1).date(),
    }
    mixin = ResponseMixinModel(redacted_response=redacted_response)
    arguments = mixin.create_model_arguments('z')

    assert arguments['date_response'] is None

def test__response__create_model_arguments__missing_date():
    """Confirms handling when transaction_date missing."""
    redacted_response = {
        'transaction_time': datetime(2018, 1, 1, 12, 0).time(),
    }
    mixin = ResponseMixinModel(redacted_response=redacted_response)
    arguments = mixin.create_model_arguments('z')

    assert arguments['date_response'] is None

@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
def test__response__save_transaction():
    """Tests handling of a valid save_transaction call."""
    response = {
        'transaction_success': True,
        'response_message': 'APPROVED',
        'notice': '',
        'raw_request': 'cardHolderName=a&cardToken=b',
        'raw_response': (
            '<cardHolderName>a</cardHolderName><cardToken>b</cardToken>'
        ),
        'cc_name': 'a',
        'token': 'b',
    }
    mixin = ResponseMixinModel(response=response)
    model_instance = mixin.save_transaction('s')

    assert isinstance(model_instance, MockDjangoModel)


@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
def test__response__save_transaction__with_redacted_data():
    """Tests handling of save_transaction call when redacted data present."""
    response = {
        'transaction_success': True,
        'response_message': 'APPROVED',
        'notice': '',
        'raw_request': 'cardHolderName=a&cardToken=b',
        'raw_response': (
            '<cardHolderName>a</cardHolderName><cardToken>b</cardToken>'
        ),
        'cc_name': 'a',
    }
    redacted_response = {
        'transaction_success': True,
        'response_message': 'APPROVED',
        'notice': '',
        'raw_request': 'cardHolderName=REDACTED',
        'raw_response': (
            '<cardHolderName>REDACTED</cardHolderName>'
        ),
        'cc_name': 'REDACTED',
    }
    mixin = ResponseMixinModel(
        response=response, redacted_response=redacted_response
    )
    model_instance = mixin.save_transaction('s')

    assert isinstance(model_instance, MockDjangoModel)

@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    mock_integrity_error
)
def test__response__save_transaction__integrity_error():
    """Tests handling when there is an IntegrityError."""
    mixin = ResponseMixinModel(response={})

    try:
        mixin.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    mock_value_error
)
def test__response__save_transaction__value_error():
    """Tests handling when there is a ValueError."""
    mixin = ResponseMixinModel(response={})

    try:
        mixin.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

@patch(
    'helcim.models.HelcimToken.objects.get_or_create',
    mock_get_or_create_created
)
@patch.dict(
    'helcim.mixins.SETTINGS',
    {'redact_cc_name': False, 'redact_cc_expiry': False}
)
def test__response__save_token():
    """Tests that expected details are provided to HelcimToken model."""
    response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'cc_name': 'Test Name',
        'cc_expiry': '0120',
        'customer_code': 'CST1000',
    }
    mixin = ResponseMixinModel(response=response, save_token=True)

    token_instance = mixin.save_token_to_vault()

    # Checks that all proper fields ended up getting passed to model
    assert token_instance.data['token'] == 'abcdefghijklmnopqrstuvw'
    assert token_instance.data['token_f4l4'] == '11119999'
    assert token_instance.data['cc_name'] == 'Test Name'
    assert token_instance.data['cc_expiry'] == date(year=2020, month=1, day=31)
    assert token_instance.data['customer_code'] == 'CST1000'
    assert token_instance.data['django_user'] is None

def test__response__save_token__missing_token():
    """Tests that None is returned when there is no token to save."""
    response = {
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    mixin = ResponseMixinModel(response=response, save_token=True)

    token_instance = mixin.save_token_to_vault()

    # Checks that None is returned
    assert token_instance is None

def test__response__save_token__missing_token_f4l4():
    """Tests that None is returned when there is no F4L4 details."""
    response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
    }
    mixin = ResponseMixinModel(response=response, save_token=True)

    token_instance = mixin.save_token_to_vault()

    # Checks that None is returned
    assert token_instance is None

def test__response__save_token__missing_customer_code():
    """Tests that error returned if no customer_code provided."""
    response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
    }
    mixin = ResponseMixinModel(response=response, save_token=True)

    try:
        mixin.save_token_to_vault()
    except helcim_exceptions.ProcessingError as error:
        assert str(error) == (
            'Unable to save token - customer code not provided'
        )
    else:
        assert False

@patch(
    'helcim.models.HelcimToken.objects.get_or_create',
    mock_get_or_create_created
)
@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': False})
def test__response__save_token__with_django_user(user):
    """Tests that HelcimToken associated to provided user."""
    response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    mixin = ResponseMixinModel(
        django_user=user, response=response, save_token=True
    )

    token_instance = mixin.save_token_to_vault()

    # Confirm user was associated to model instance
    assert token_instance.data['django_user'] == user

    # Checks that other fields ended up getting passed to model
    assert token_instance.data['token'] == 'abcdefghijklmnopqrstuvw'
    assert token_instance.data['token_f4l4'] == '11119999'
    assert token_instance.data['customer_code'] == 'CST1000'

@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': False})
def test__response__save_token__with_django_user_not_provided():
    """Tests that error raised when user not provided when required."""
    response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    mixin = ResponseMixinModel(
        django_user=None, response=response, save_token=True
    )

    try:
        mixin.save_token_to_vault()
    except helcim_exceptions.ProcessingError as error:
        assert str(error) == 'Required Django user reference not provided.'
    else:
        assert False

@patch(
    'helcim.models.HelcimToken.objects.get_or_create',
    mock_get_or_create_created
)
@patch.dict('helcim.mixins.SETTINGS', {'allow_anonymous': True})
def test__response__save_token__with_customer_code():
    """Tests that token can be saved by customer code alone when allowed."""
    response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    mixin = ResponseMixinModel(
        django_user=None, response=response, save_token=True
    )

    token_instance = mixin.save_token_to_vault()

    # Checks that no user is added
    assert token_instance.data['django_user'] is None

    # Confirm all other details provided to token
    assert token_instance.data['token'] == 'abcdefghijklmnopqrstuvw'
    assert token_instance.data['token_f4l4'] == '11119999'
    assert token_instance.data['customer_code'] == 'CST1000'

@patch.dict('helcim.mixins.SETTINGS', {'helcim_js': {'id': {'url': 'abc'}}})
def test__helcim_js_mixin__adds_context():
    """Confirms that expected context is added with mixin."""
    django_view = MockMixinView()

    context = django_view.get_context_data()

    assert 'helcim_js' in context
    assert context['helcim_js'] == {'id': {'url': 'abc', 'test_input': ''}}

@patch.dict('helcim.mixins.SETTINGS', {'helcim_js': {'id': {'test': True}}})
def test__helcim_js_mixin__adds_test_input__with_test_key():
    """Confirms an HTML test input is added when test key specified."""
    django_view = MockMixinView()

    context = django_view.get_context_data()

    assert 'test_input' in context['helcim_js']['id']
    assert context['helcim_js']['id']['test_input'] == str(
        '<input id="test" type="hidden" value="1">'
    )
    assert isinstance(context['helcim_js']['id']['test_input'], SafeString)

@patch.dict('helcim.mixins.SETTINGS', {'helcim_js': {'id': {}}})
def test__helcim_js_mixin__adds_test_input__without_test_key():
    """Confirms empty string returned when test key not specified."""
    django_view = MockMixinView()

    context = django_view.get_context_data()

    assert 'test_input' in context['helcim_js']['id']
    assert context['helcim_js']['id']['test_input'] == ''

@patch.dict('helcim.mixins.SETTINGS', {'helcim_js': {'id': {'test': False}}})
def test__helcim_js_mixin__adds_test_input__with_falsy_key():
    """Confirms empty string returned when test key is a falsy value."""
    django_view = MockMixinView()

    context = django_view.get_context_data()

    assert 'test_input' in context['helcim_js']['id']
    assert context['helcim_js']['id']['test_input'] == ''
