"""Tests for the HelcimJSResponse object.

    Majority of tests will be done as integration tests, as there is minimal
    value confirming the "record" methods function.
"""
# pylint: disable=protected-access
from unittest.mock import patch, MagicMock

from helcim.gateway import HelcimJSResponse
from helcim.exceptions import HelcimError


def test__record_response__unvalidated_data():
    """Confirms exception raised when saving unvalidated data."""
    response = HelcimJSResponse('')
    response.validated = False
    response.valid = False

    try:
        response._record_response('s')
    except HelcimError as error:
        assert str(error) == (
            'Must validate data with the .is_valid() method '
            ' before recording purchase.'
        )
    else:
        assert False

def test__record_response__invalid_data():
    """Confirms exception raised when saving invalid data."""
    response = HelcimJSResponse('')
    response.validated = True
    response.valid = False

    try:
        response._record_response('s')
    except HelcimError as error:
        assert str(error) == (
            'Response data was invalid - cannot record purchase data.'
        )
    else:
        assert False

@patch(
    'helcim.conversions.process_helcim_js_response',
    MagicMock(return_value={'transaction_success': True}),
)
def test__is_valid__valid():
    """Confirms method returns True when successful response returned."""
    response = HelcimJSResponse('')

    # Confirm validated and valid attributes are false by defualt
    assert response.validated is False
    assert response.valid is False

    # Validate and confirm attributes update
    assert response.is_valid() is True
    assert response.validated is True
    assert response.valid is True

@patch(
    'helcim.conversions.process_helcim_js_response',
    MagicMock(return_value={'transaction_success': False}),
)
def test__is_valid__invalid():
    """Confirms method returns False when unsuccessful response returned."""
    response = HelcimJSResponse('')

    # Confirm validated and valid attributes are false by defualt
    assert response.validated is False
    assert response.valid is False

    # Validate and confirm attributes update
    assert response.is_valid() is False
    assert response.validated is True
    assert response.valid is False

@patch.dict('helcim.mixins.SETTINGS', {'redact_all': True, })
def test__is_valid__redactions_applied():
    """Confirm that all redactions are applied during validation.

        Don't need to worry about API details or raw_request, because
        these details will not be part of a Helcim.js response.
    """
    raw_request = {
        'response': '1',
        'cardHolderName': 'TEST NAME',
        'cardNumber': '1111 **** **** 9999',
        'cardExpiry': '0150',
        'cardType': 'Mastercard',
        'cardToken': '123456789abcdefghijk',
        'xml': (
            '<message>'
            '<response>1</response>'
            '<cardHolderName>TEST NAME</cardHolderName>'
            '<cardNumber>1111 **** **** 9999</cardNumber>'
            '<cardExpiry>0820</cardExpiry><expiryDate>REDACTED</expiry>'
            '<cardToken>123456789abcdefghijk</cardToken>'
            '<cardF4L4>REDACTED</cardF4L4>'
            '<cardType>Mastercard</cardType>'
            '</message>'
        ),
    }
    response = HelcimJSResponse(raw_request)

    assert response.is_valid()

    raw_response = response.redacted_response['raw_response']

    redacted_cc_name = '<cardHolderName>REDACTED</cardHolderName>'
    assert redacted_cc_name in raw_response
    assert response.redacted_response['cc_name'] is None

    redacted_cc_number = '<cardNumber>REDACTED</cardNumber>'
    assert redacted_cc_number in raw_response
    assert response.redacted_response['cc_number'] is None

    redacted_cc_expiry = (
        '<cardExpiry>REDACTED</cardExpiry><expiryDate>REDACTED</expiry>'
    )
    assert redacted_cc_expiry in raw_response
    assert response.redacted_response['cc_expiry'] is None

    redacted_cc_type = '<cardType>REDACTED</cardType>'
    assert redacted_cc_type in raw_response
    assert response.redacted_response['cc_type'] is None

    redacted_token = (
        '<cardToken>REDACTED</cardToken><cardF4L4>REDACTED</cardF4L4>'
    )
    assert redacted_token in raw_response
    assert response.redacted_response['token'] is None
    assert response.redacted_response['token_f4l4'] is None
