"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access

from unittest.mock import patch

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
                    <type>preauth</type>
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
@patch(
    'helcim.gateway.models.HelcimTransaction.objects.create',
    MockDjangoModel
)
def test_capture_processing():
    details = {
        'transaction_id': 1,
    }

    capture = gateway.Capture(api_details=API_DETAILS, **details)
    response = capture.process()

    assert isinstance(response, MockDjangoModel)

def test_process_error_response_capture():
    capture_request = gateway.Capture()

    try:
        capture_request.process_error_response('')
    except helcim_exceptions.PaymentError:
        assert True
    else:
        assert False

def test_validate_preauth_transaction_invalid():
    capture = gateway.Capture(api_details=API_DETAILS, **{})

    try:
        capture.validate_preauth_transaction()
    except helcim_exceptions.PaymentError:
        assert True
    else:
        assert False

def test_validate_preauth_transaction_valid():
    details = {'transaction_id': 1}
    capture = gateway.Capture(api_details=API_DETAILS, **details)

    try:
        capture.validate_preauth_transaction()
    except helcim_exceptions.PaymentError:
        assert False
    else:
        assert True
