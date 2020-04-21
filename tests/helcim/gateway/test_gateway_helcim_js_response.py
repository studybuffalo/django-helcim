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
