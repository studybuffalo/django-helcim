"""Tests for the HelcimJSResponse object.

    Majority of tests will be done as integration tests, as there is minimal
    value confirming the "record" methods function.
"""
from unittest.mock import patch, MagicMock

from helcim.gateway import HelcimJSResponse


@patch(
    'helcim.conversions.process_helcim_js_response',
    MagicMock(return_value={'transaction_success': True}),
)
def test__is_valid__valid():
    """Confirms method returns True when successful response returned."""
    response = HelcimJSResponse('')

    assert response.is_valid() is True

@patch(
    'helcim.conversions.process_helcim_js_response',
    MagicMock(return_value={'transaction_success': False}),
)
def test__is_valid__invalid():
    """Confirms method returns False when unsuccessful response returned."""
    response = HelcimJSResponse('')

    assert response.is_valid() is False
