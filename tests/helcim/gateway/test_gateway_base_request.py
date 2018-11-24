"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access
from datetime import datetime
from unittest.mock import patch

import requests

from django.db import IntegrityError
from django.test import override_settings

from helcim import exceptions as helcim_exceptions, gateway


class MockPostResponse():
    def __init__(self, url, data):
        self.text = """<?xml version="1.0"?>
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
        self.text = """<?xml version="1.0"?>
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

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'api_url': '1', 'account_id': '2', 'api_token': '3', 'terminal_id': '4',}
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
@patch.dict('helcim.gateway.SETTINGS', {'api_url': '1'})
def test_set_api_details_argument_overrides_settings():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    assert 'url' in base.api
    assert base.api['url'] == 'https://www.test.com'

def test_configure_test_transaction_in_data():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.cleaned = {'test': True}

    base.configure_test_transaction()

    assert 'test' in base.cleaned
    assert base.cleaned['test'] is True

@patch.dict('helcim.gateway.SETTINGS', {'api_test': False})
def test_configure_test_transaction_data_overrides_settings():
    base = gateway.BaseRequest(api_details=API_DETAILS)
    base.cleaned = {'test': True}

    base.configure_test_transaction()

    assert base.cleaned['test'] is True

@patch.dict('helcim.gateway.SETTINGS', {'api_test': True})
def test_configure_test_transaction_setting():
    base = gateway.BaseRequest(api_details=API_DETAILS)

    base.configure_test_transaction()

    assert base.cleaned['test'] is True

def test_identify_redact_fields_defaults():
    fields = gateway.identify_redact_fields()

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
def test_identify_redact_fields_redact_all_true():
    fields = gateway.identify_redact_fields()

    assert fields['name']['redact'] is True
    assert fields['number']['redact'] is True
    assert fields['expiry']['redact'] is True
    assert fields['cvv']['redact'] is True
    assert fields['type']['redact'] is True
    assert fields['token']['redact'] is True
    assert fields['mag']['redact'] is True
    assert fields['mag_enc']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_all': False})
def test_identify_redact_fields_redact_all_false():
    fields = gateway.identify_redact_fields()

    assert fields['name']['redact'] is False
    assert fields['number']['redact'] is False
    assert fields['expiry']['redact'] is False
    assert fields['cvv']['redact'] is False
    assert fields['type']['redact'] is False
    assert fields['token']['redact'] is False
    assert fields['mag']['redact'] is False
    assert fields['mag_enc']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_name': True})
def test_identify_redact_fields_redact_name_true():
    fields = gateway.identify_redact_fields()

    assert fields['name']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_name': False})
def test_identify_redact_fields_redact_name_false():
    fields = gateway.identify_redact_fields()

    assert fields['name']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_number': True})
def test_identify_redact_fields_redact_number_true():
    fields = gateway.identify_redact_fields()

    assert fields['number']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_number': False})
def test_identify_redact_fields_redact_number_false():
    fields = gateway.identify_redact_fields()

    assert fields['number']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_expiry': True})
def test_identify_redact_fields_redact_expiry_true():
    fields = gateway.identify_redact_fields()

    assert fields['expiry']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_expiry': False})
def test_identify_redact_fields_redact_expiry_false():
    fields = gateway.identify_redact_fields()

    assert fields['expiry']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_cvv': True})
def test_identify_redact_fields_redact_cvv_true():
    fields = gateway.identify_redact_fields()

    assert fields['cvv']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_cvv': False})
def test_identify_redact_fields_redact_cvv_false():
    fields = gateway.identify_redact_fields()

    assert fields['cvv']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_type': True})
def test_identify_redact_fields_redact_type_true():
    fields = gateway.identify_redact_fields()

    assert fields['type']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_type': False})
def test_identify_redact_fields_redact_type_false():
    fields = gateway.identify_redact_fields()

    assert fields['type']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_token': True})
def test_identify_redact_fields_redact_token_true():
    fields = gateway.identify_redact_fields()

    assert fields['token']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_token': False})
def test_identify_redact_fields_redact_token_false():
    fields = gateway.identify_redact_fields()

    assert fields['token']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic': True})
def test_identify_redact_fields_redact_mag_true():
    fields = gateway.identify_redact_fields()

    assert fields['mag']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic': False})
def test_identify_redact_fields_redact_mag_false():
    fields = gateway.identify_redact_fields()

    assert fields['mag']['redact'] is False

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic_encrypted': True})
def test_identify_redact_fields_redact_mag_enc_true():
    fields = gateway.identify_redact_fields()

    assert fields['mag_enc']['redact'] is True

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_magnetic_encrypted': False})
def test_identify_redact_fields_redact_mag_enc_false():
    fields = gateway.identify_redact_fields()

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
def test_identify_redact_fields_redact_all_true_overrides():
    fields = gateway.identify_redact_fields()

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
def test_identify_redact_fields_redact_all_false_overrides():
    fields = gateway.identify_redact_fields()

    assert fields['name']['redact'] is False
    assert fields['number']['redact'] is False
    assert fields['expiry']['redact'] is False
    assert fields['cvv']['redact'] is False
    assert fields['type']['redact'] is False
    assert fields['token']['redact'] is False
    assert fields['mag']['redact'] is False
    assert fields['mag_enc']['redact'] is False

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

def test_redact_field_only_redacts_specified_details():
    base = gateway.BaseRequest()
    base.redacted_response = {
        'raw_request': 'cardHolderName=a',
        'raw_response': '<cardHolderName>a</cardHolderName>',
        'cc_name': 'a',
    }
    base._redact_field('cardNumber', 'cc_number')

    assert len(base.redacted_response) == 3
    assert base.redacted_response['raw_request'] == 'cardHolderName=a'
    assert base.redacted_response['raw_response'] == (
        '<cardHolderName>a</cardHolderName>'
    )
    assert base.redacted_response['cc_name'] is 'a'

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_name': True})
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

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_number': True})
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

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_expiry': True})
def test_redact_data_cc_expiry():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardExpiry=a',
        'raw_response': '<cardExpiry>a</cardExpiry><expiryDate>b</expiryDate>',
        'cc_expiry': 'a',
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == 'cardExpiry=REDACTED'
    assert base.redacted_response['raw_response'] == (
        '<cardExpiry>REDACTED</cardExpiry><expiryDate>REDACTED</expiryDate>'
    )
    assert base.redacted_response['cc_expiry'] is None

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_type': True})
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

@patch.dict('helcim.gateway.SETTINGS', {'redact_token': True})
def test_redact_data_token():
    base = gateway.BaseRequest()
    base.response = {
        'raw_request': 'cardToken=a&cardF4L4=11119999',
        'raw_response': (
            '<cardToken>a</cardToken><cardF4L4>11119999</cardF4L4>'
        ),
        'token': 'a',
        'token_f4l4': '11119999'
    }
    base.redact_data()

    assert base.redacted_response['raw_request'] == (
        'cardToken=REDACTED&cardF4L4=REDACTED'
    )
    assert base.redacted_response['raw_response'] == (
        '<cardToken>REDACTED</cardToken><cardF4L4>REDACTED</cardF4L4>'
    )
    assert base.redacted_response['token'] is None
    assert base.redacted_response['token_f4l4'] is None

@patch.dict('helcim.gateway.SETTINGS', {'redact_cc_name': True})
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
    MockDjangoModel
)
def test_save_transaction_with_redacted_data():
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
    }
    base.redacted_response = {
        'transaction_success': True,
        'response_message': 'APPROVED',
        'notice': '',
        'raw_request': 'cardHolderName=REDACTED',
        'raw_response': (
            '<cardHolderName>REDACTED</cardHolderName>'
        ),
        'cc_name': 'REDACTED',
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

    assert len(arguments) == 21
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
        'token_f4l4': 'm',
        'avs_response': 'n',
        'cvv_response': 'o',
        'approval_code': 'p',
        'order_number': 'q',
        'customer_code': 'r',
    }

    arguments = base.create_model_arguments('z')

    assert len(arguments) == 21
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
    assert arguments['token_f4l4'] == 'm'
    assert arguments['avs_response'] == 'n'
    assert arguments['cvv_response'] == 'o'
    assert arguments['approval_code'] == 'p'
    assert arguments['order_number'] == 'q'
    assert arguments['customer_code'] == 'r'
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
