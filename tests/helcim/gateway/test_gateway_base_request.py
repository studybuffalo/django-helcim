"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access
from datetime import datetime
from unittest.mock import patch

import requests

from django.conf import settings
from django.core import exceptions as django_exceptions
from django.db import IntegrityError
from django.test import override_settings

from helcim import exceptions as helcim_exceptions, gateway


class MockPostResponse():
    def __init__(self, url, data):
        self.content = """<?xml version="1.0"?>
            <message>
                <response>1</response>
                <responseMessage>APPROVED</responseMessage>
                <notice></notice>
                <transaction>
                    <transactionId>1111111</transactionId>
                    <type>purchase</type>
                    <date>2018-01-01</date>
                    <time>12:00:00</time>
                    <cardHolderName>Test Person</cardHolderName>
                    <amount>100.00</amount>
                    <currency>CAD</currency>
                    <cardNumber>5454********5454</cardNumber>
                    <cardToken>80defad45bae30e557da0e</cardToken>
                    <expiryDate>0125</expiryDate>
                    <cardType>MasterCard</cardType>
                    <avsResponse>X</avsResponse>
                    <cvvResponse>M</cvvResponse>
                    <approvalCode>T6E1ST</approvalCode>
                    <orderNumber>INV1000</orderNumber>
                    <customerCode>CST1000</customerCode>
                </transaction>
            </message>
            """
        self.status_code = 200
        self.url = url
        self.data = data

def mock_post_api_error(url, data): # pylint: disable=unused-argument
    raise requests.ConnectionError

class MockPostAPINon200StatusCode():
    def __init__(self, url, data):
        self.status_code = 404
        self.content = """<?xml version="1.0"?>
            <message>
                <response>0</response>
                <responseMessage>Error Message Goes Here</responseMessage>
            </message>
            """
        self.url = url
        self.data = data

class MockPostAPIErrorResponse():
    def __init__(self, url, data):
        self.status_code = 200
        self.content = """<?xml version="1.0"?>
            <message>
                <response>0</response>
                <responseMessage>TEST ERROR</responseMessage>
            </message>
            """
        self.url = url
        self.data = data

class MockDjangoModel():
    def __init__(self, **kwargs):
        self.data = kwargs

def mock_integrity_error(**kwargs): # pylint: disable=unused-argument
    raise IntegrityError

API_DETAILS = {
    'url': 'https://www.test.com',
    'account_id': '12345678',
    'token': 'abcdefg',
    'terminal_id': '98765432',
}

@patch('helcim.gateway.requests.post', MockPostResponse)
def test_post_returns_dictionary():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.post()

    assert isinstance(base.response, dict)

@patch('helcim.gateway.requests.post', mock_post_api_error)
def test_post_api_connection_error():
    base_request = gateway.BaseRequest(api_details=API_DETAILS)

    try:
        base_request.post()
    except helcim_exceptions.ProcessingError as error:
        assert True
        assert str(error) == (
            "Unable to connect to Helcim API (https://www.test.com)"
        )
    else:
        assert False

@patch('helcim.gateway.requests.post', MockPostAPINon200StatusCode)
def test_post_api_non_200_status_code():
    base_request = gateway.BaseRequest(api_details=API_DETAILS)

    try:
        base_request.post()
    except helcim_exceptions.ProcessingError as error:
        assert True
        assert str(error) == "Helcim API request failed with status code 404"
    else:
        assert False

@patch('helcim.gateway.requests.post', MockPostAPIErrorResponse)
def test_post_api_error_response_message():
    base_request = gateway.BaseRequest(api_details=API_DETAILS)

    try:
        base_request.post()
    except helcim_exceptions.HelcimError as error:
        assert True
        assert str(error) == "Helcim API request failed: TEST ERROR"
    else:
        assert False

def test_process_error_response_base():
    base_request = gateway.BaseRequest()

    try:
        base_request.process_error_response('')
    except helcim_exceptions.HelcimError:
        assert True
    else:
        assert False

def test_set_api_details_argument():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    assert 'url' in base.api
    assert base.api['url'] == 'https://www.test.com'
    assert 'account_id' in base.api
    assert base.api['account_id'] == '12345678'
    assert 'token' in base.api
    assert base.api['token'] == 'abcdefg'
    assert 'terminal_id' in base.api
    assert base.api['terminal_id'] == '98765432'

@override_settings(
    HELCIM_API_URL='1',
    HELCIM_ACCOUNT_ID='2',
    HELCIM_API_TOKEN='3',
    HELCIM_TERMINAL_ID='4'
)
def test_set_api_details_settings():
    base = gateway.BaseRequest()

    assert 'url' in base.api
    assert base.api['url'] == '1'
    assert 'account_id' in base.api
    assert base.api['account_id'] == '2'
    assert 'token' in base.api
    assert base.api['token'] == '3'
    assert 'terminal_id' in base.api
    assert base.api['terminal_id'] == '4'

@override_settings(HELCIM_API_URL=1)
def test_set_api_details_argument_overrides_settings():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    assert 'url' in base.api
    assert base.api['url'] == 'https://www.test.com'

@override_settings()
def test_set_api_details_no_account_id():
    del settings.HELCIM_ACCOUNT_ID

    try:
        gateway.BaseRequest()
    except django_exceptions.ImproperlyConfigured as error:
        assert True
        assert str(error) == 'You must define a HELCIM_ACCOUNT_ID setting'
    else:
        assert False

@override_settings()
def test_set_api_details_no_api_token():
    del settings.HELCIM_API_TOKEN

    try:
        gateway.BaseRequest()
    except django_exceptions.ImproperlyConfigured as error:
        assert True
        assert str(error) == 'You must define a HELCIM_API_TOKEN setting'
    else:
        assert False

@override_settings()
def test_set_api_details_none():
    del settings.HELCIM_API_URL
    del settings.HELCIM_ACCOUNT_ID
    del settings.HELCIM_API_TOKEN
    del settings.HELCIM_TERMINAL_ID

    try:
        gateway.BaseRequest()
    except django_exceptions.ImproperlyConfigured:
        assert True
    else:
        assert False

def test_configure_test_transaction_in_data():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.cleaned = {'test': True}

    base.configure_test_transaction()

    assert 'test' in base.cleaned
    assert base.cleaned['test'] is True

@override_settings(HELCIM_API_TEST=False)
def test_configure_test_transaction_data_overrides_settings():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.cleaned = {'test': True}

    base.configure_test_transaction()

    assert base.cleaned['test'] is True

@override_settings(HELCIM_API_TEST=True)
def test_configure_test_transaction_setting():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    base.configure_test_transaction()

    assert base.cleaned['test'] is True

@override_settings()
def test_configure_test_transaction_not_set():
    del settings.HELCIM_API_TEST
    base = gateway.BaseRequest(api_details=API_DETAILS)

    base.configure_test_transaction()

    assert 'test' not in base.cleaned

@override_settings(HELCIM_REDACT_ALL=True)
def test_identify_redact_fields_redact_all():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is True
    assert fields['number'] is True
    assert fields['expiry'] is True
    assert fields['type'] is True
    assert fields['token'] is True

@override_settings(HELCIM_REDACT_CC_NAME=True)
def test_identify_redact_fields_redact_name():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is True
    assert fields['number'] is False
    assert fields['expiry'] is False
    assert fields['type'] is False
    assert fields['token'] is False

@override_settings(HELCIM_REDACT_CC_NUMBER=True)
def test_identify_redact_fields_redact_number():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is True
    assert fields['expiry'] is False
    assert fields['type'] is False
    assert fields['token'] is False

@override_settings(HELCIM_REDACT_CC_EXPIRY=True)
def test_identify_redact_fields_redact_expiry():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is False
    assert fields['expiry'] is True
    assert fields['type'] is False
    assert fields['token'] is False

@override_settings(HELCIM_REDACT_CC_TYPE=True)
def test_identify_redact_fields_redact_type():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is False
    assert fields['expiry'] is False
    assert fields['type'] is True
    assert fields['token'] is False

@override_settings(HELCIM_REDACT_TOKEN=True)
def test_identify_redact_fields_redact_token():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is False
    assert fields['expiry'] is False
    assert fields['type'] is False
    assert fields['token'] is True

@override_settings(HELCIM_REDACT_ALL=True, HELCIM_REDACT_CC_NAME=False)
def test_identify_redact_fields_redact_all_with_individual():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is True

def test_redact_api_data_account_id():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'raw_request': 'accountId=1',
    }
    base._redact_api_data()

    assert base.redacted_response['raw_request'] == 'accountId=REDACTED'

def test_redact_api_data_api_token():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'raw_request': 'apiToken=1',
    }
    base._redact_api_data()

    assert base.redacted_response['raw_request'] == 'apiToken=REDACTED'

def test_redact_api_data_terminal_id():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'raw_request': 'terminalId=1',
    }
    base._redact_api_data()

    assert base.redacted_response['raw_request'] == 'terminalId=REDACTED'

def test_redact_api_data_all_fields():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'raw_request': 'accountId=1&apiToken=2&terminalId=3',
    }
    base._redact_api_data()

    assert base.redacted_response['raw_request'] == (
        'accountId=REDACTED&apiToken=REDACTED&terminalId=REDACTED'
    )

def test_redact_api_data_no_raw_request():
    base = gateway.BaseRequest()
    base.redacted_response = {}
    base._redact_api_data()

    assert base.redacted_response['raw_request'] is None

def test_redact_field():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    base._redact_field('cardHolderName', 'cc_name')

    assert base.redacted_response['raw_request'] == 'cardHolderName=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName>'
    )
    assert base.redacted_response['cc_name'] is None

@override_settings(HELCIM_REDACT_CC_NAME=True)
def test_redact_data_cc_name():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == 'cardHolderName=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName>'
    )
    assert base.redacted_response['cc_name'] is None

@override_settings(HELCIM_REDACT_CC_NUMBER=True)
def test_redact_data_cc_number():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardNumber=a',
        'raw_response': '<cardNumber>a</cardNumber>',
        'cc_number': 'a',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == 'cardNumber=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardNumber>REDACTED</cardNumber>'
    )
    assert base.redacted_response['cc_number'] is None

@override_settings(HELCIM_REDACT_CC_EXPIRY=True)
def test_redact_data_cc_expiry():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'expiryDate=a',
        'raw_response': '<expiryDate>a</expiryDate>',
        'cc_expiry': 'a',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == 'expiryDate=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<expiryDate>REDACTED</expiryDate>'
    )
    assert base.redacted_response['cc_expiry'] is None

@override_settings(HELCIM_REDACT_CC_TYPE=True)
def test_redact_data_cc_type():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardType=a',
        'raw_response': '<cardType>a</cardType>',
        'cc_type': 'a',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == 'cardType=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardType>REDACTED</cardType>'
    )
    assert base.redacted_response['cc_type'] is None

@override_settings(HELCIM_REDACT_TOKEN=True)
def test_redact_data_token():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardToken=a',
        'raw_response': '<cardToken>a</cardToken>',
        'token': 'a',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == 'cardToken=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardToken>REDACTED</cardToken>'
    )
    assert base.redacted_response['token'] is None

# TODO: Create test to ensure the f4l4 field is redacted as well

@override_settings(HELCIM_REDACT_CC_NAME=True)
def test_redact_data_partial():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardHolderName=a&cardToken=b',
        'raw_response': (
            '<cardHolderName>a</cardHolderName><cardToken>b</cardToken>'
        ),
        'cc_name': 'a',
        'token': 'b',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == (
        'cardHolderName=REDACTED&cardToken=b'
    )
    assert base.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName><cardToken>b</cardToken>'
    )
    assert base.redacted_response['cc_name'] is None
    assert base.redacted_response['token'] == 'b'

@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
def test_save_transaction():
    base = gateway.BaseRequest()
    base.response = {
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
    model_instance = base.save_transaction('s')

    assert isinstance(model_instance, MockDjangoModel)

@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    mock_integrity_error
)
def test_save_transaction_integrity_error():
    base = gateway.BaseRequest()
    base.response = {}

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

def test_convert_expiry_to_date():
    base = gateway.BaseRequest()

    expiry = base.convert_expiry_to_date('0118')

    assert expiry == datetime(18, 1, 31).date()

def test_create_model_arguments_partial():
    base = gateway.BaseRequest()
    base.redacted_response = {}

    arguments = base.create_model_arguments('z')

    assert len(arguments) == 20
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

def test_create_model_arguments_full():
    base = gateway.BaseRequest()
    base.redacted_response = {
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
        'avs_response': 'm',
        'cvv_response': 'n',
        'approval_code': 'o',
        'order_number': 'p',
        'customer_code': 'q',
    }

    arguments = base.create_model_arguments('z')

    assert len(arguments) == 20
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
    assert arguments['cc_expiry'] == datetime(20, 6, 30).date()
    assert arguments['cc_type'] == 'k'
    assert arguments['token'] == 'l'
    assert arguments['avs_response'] == 'm'
    assert arguments['cvv_response'] == 'n'
    assert arguments['approval_code'] == 'o'
    assert arguments['order_number'] == 'p'
    assert arguments['customer_code'] == 'q'
    assert arguments['transaction_type'] == 'z'

def test_create_model_arguments_missing_time():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'transaction_date': datetime(2018, 1, 1).date(),
    }

    arguments = base.create_model_arguments('z')

    assert arguments['date_response'] is None

def test_create_model_arguments_missing_date():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'transaction_time': datetime(2018, 1, 1, 12, 0).time(),
    }

    arguments = base.create_model_arguments('z')

    assert arguments['date_response'] is None

# TODO: test that create_model_arguments formats f4l4 properly
