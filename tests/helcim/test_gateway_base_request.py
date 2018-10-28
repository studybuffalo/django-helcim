"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access

from unittest.mock import patch

import requests

from django.core import exceptions as django_exceptions

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

def test_process_error_response_purchase():
    purchase_request = gateway.Purchase()

    try:
        purchase_request.process_error_response('')
    except helcim_exceptions.PaymentError:
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

@patch('helcim.gateway.settings.HELCIM_API_URL', '1', create=True)
@patch('helcim.gateway.settings.HELCIM_ACCOUNT_ID', '2', create=True)
@patch('helcim.gateway.settings.HELCIM_API_TOKEN', '3', create=True)
@patch('helcim.gateway.settings.HELCIM_TERMINAL_ID', '4', create=True)
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

@patch('helcim.gateway.settings.HELCIM_API_URL', '1')
def test_set_api_details_argument_overrides_settings():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    assert 'url' in base.api
    assert base.api['url'] == 'https://www.test.com'

@patch('helcim.gateway.settings', None)
def test_set_api_details_none():
    try:
        gateway.BaseRequest()
    except django_exceptions.ImproperlyConfigured:
        assert True
    else:
        assert False

def test_configure_test_transaction_in_data():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.cleaned = {'test': True}

    base._configure_test_transaction()

    assert 'test' in base.cleaned
    assert base.cleaned['test'] is True

@patch('helcim.gateway.settings.HELCIM_API_TEST', False, create=True)
def test_configure_test_transaction_data_overrides_settings():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.cleaned = {'test': True}

    base._configure_test_transaction()

    assert base.cleaned['test'] is True

@patch('helcim.gateway.settings.HELCIM_API_TEST', True, create=True)
def test_configure_test_transaction_setting():
    print('run test')
    base = gateway.BaseRequest(api_details=API_DETAILS)

    base._configure_test_transaction()

    assert base.cleaned['test'] is True

@patch('helcim.gateway.settings', None)
def test_configure_test_transaction_not_set():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    base._configure_test_transaction()

    assert 'test' not in base.cleaned

@patch('helcim.gateway.settings.HELCIM_REDACT_ALL', True, create=True)
def test_identify_redact_fields_redact_all():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is True
    assert fields['number'] is True
    assert fields['expiry'] is True
    assert fields['type'] is True
    assert fields['token'] is True

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_NAME', True, create=True)
def test_identify_redact_fields_redact_name():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is True
    assert fields['number'] is False
    assert fields['expiry'] is False
    assert fields['type'] is False
    assert fields['token'] is False

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_NUMBER', True, create=True)
def test_identify_redact_fields_redact_number():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is True
    assert fields['expiry'] is False
    assert fields['type'] is False
    assert fields['token'] is False

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_EXPIRY', True, create=True)
def test_identify_redact_fields_redact_expiry():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is False
    assert fields['expiry'] is True
    assert fields['type'] is False
    assert fields['token'] is False

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_TYPE', True, create=True)
def test_identify_redact_fields_redact_type():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is False
    assert fields['expiry'] is False
    assert fields['type'] is True
    assert fields['token'] is False

@patch('helcim.gateway.settings.HELCIM_REDACT_TOKEN', True, create=True)
def test_identify_redact_fields_redact_token():
    base = gateway.BaseRequest()

    fields = base._identify_redact_fields()

    assert fields['name'] is False
    assert fields['number'] is False
    assert fields['expiry'] is False
    assert fields['type'] is False
    assert fields['token'] is True

@patch('helcim.gateway.settings.HELCIM_REDACT_ALL', True, create=True)
@patch('helcim.gateway.settings.HELCIM_REDACT_CC_NAME', False, create=True)
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

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_NAME', True, create=True)
def test_redact_data_cc_name():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    base._redact_data()

    assert base.redacted_response['raw_request'] == 'cardHolderName=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardHolderName>REDACTED</cardHolderName>'
    )
    assert base.redacted_response['cc_name'] is None

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_NUMBER', True, create=True)
def test_redact_data_cc_number():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardNumber=a',
        'raw_response': '<cardNumber>a</cardNumber>',
        'cc_number': 'a',
    }
    base._redact_data()

    assert base.redacted_response['raw_request'] == 'cardNumber=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardNumber>REDACTED</cardNumber>'
    )
    assert base.redacted_response['cc_number'] is None

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_EXPIRY', True, create=True)
def test_redact_data_cc_expiry():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'expiryDate=a',
        'raw_response': '<expiryDate>a</expiryDate>',
        'cc_expiry': 'a',
    }
    base._redact_data()

    assert base.redacted_response['raw_request'] == 'expiryDate=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<expiryDate>REDACTED</expiryDate>'
    )
    assert base.redacted_response['cc_expiry'] is None

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_TYPE', True, create=True)
def test_redact_data_cc_type():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardType=a',
        'raw_response': '<cardType>a</cardType>',
        'cc_type': 'a',
    }
    base._redact_data()

    assert base.redacted_response['raw_request'] == 'cardType=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardType>REDACTED</cardType>'
    )
    assert base.redacted_response['cc_type'] is None

@patch('helcim.gateway.settings.HELCIM_REDACT_TOKEN', True, create=True)
def test_redact_data_token():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardToken=a',
        'raw_response': '<cardToken>a</cardToken>',
        'token': 'a',
    }
    base._redact_data()

    assert base.redacted_response['raw_request'] == 'cardToken=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardToken>REDACTED</cardToken>'
    )
    assert base.redacted_response['token'] is None

@patch('helcim.gateway.settings.HELCIM_REDACT_CC_NAME', True, create=True)
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
    base._redact_data()

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
        'raw_request': 'cardHolderName=a&cardToken=b',
        'raw_response': (
            '<cardHolderName>a</cardHolderName><cardToken>b</cardToken>'
        ),
        'cc_name': 'a',
        'token': 'b',
    }
    model_instance = base.save_transaction('s')

    assert isinstance(model_instance, MockDjangoModel)
