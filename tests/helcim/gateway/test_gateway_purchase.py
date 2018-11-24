"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access
from unittest.mock import patch

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
                    <cardNumber>1111********9999</cardNumber>
                    <cardToken>abcdefghijklmnopqrstuvw</cardToken>
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

class MockDjangoModel():
    def __init__(self, **kwargs):
        self.data = kwargs

def mock_get_or_create_created(**kwargs):
    return (MockDjangoModel(**kwargs), True)

API_DETAILS = {
    'url': 'https://www.test.com',
    'account_id': '12345678',
    'token': 'abcdefg',
    'terminal_id': '98765432',
}

@patch('helcim.gateway.requests.post', MockPostResponse)
@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
def test_purchase_processing():
    details = {
        'amount': 100.00,
        'customer_code': 'CST1000',
    }

    purchase = gateway.Purchase(api_details=API_DETAILS, **details)
    transaction, _ = purchase.process()

    assert isinstance(transaction, MockDjangoModel)

def test_process_error_response_purchase():
    purchase_request = gateway.Purchase()

    try:
        purchase_request.process_error_response('')
    except helcim_exceptions.PaymentError:
        assert True
    else:
        assert False

@patch('helcim.gateway.requests.post', MockPostResponse)
@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
@patch(
    'helcim.gateway.models.HelcimToken.objects.get_or_create',
    mock_get_or_create_created
)
@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS', {'enable_token_vault': True}
)
def test_process_with_save_token_enabled():
    details = {
        'amount': 100.00,
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }

    purchase = gateway.Purchase(
        api_details=API_DETAILS, save_token=True, **details
    )
    _, token = purchase.process()

    assert isinstance(token, MockDjangoModel)

@patch('helcim.gateway.requests.post', MockPostResponse)
@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS', {'enable_token_vault': False}
)
def test_process_with_save_token_disabled():
    details = {
        'amount': 100.00,
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }

    purchase = gateway.Purchase(
        api_details=API_DETAILS, save_token=True, **details
    )
    _, token = purchase.process()

    assert token is None
