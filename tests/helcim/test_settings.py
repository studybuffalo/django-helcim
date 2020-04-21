"""Tests for the determine_helcim_settings function."""
from django.conf import settings
from django.core import exceptions as django_exceptions
from django.test import override_settings

from helcim.settings import (
    determine_helcim_settings, _validate_helcim_js_settings
)


def test__validate_helcim_js_settings__valid():
    """Confirms no errors when settings are properly set."""
    try:
        _validate_helcim_js_settings({'example': {'url': 'a', 'token': 'b'}})
    except django_exceptions.ImproperlyConfigured:
        assert False
    else:
        assert True

def test__validate_helcim_js_settings__invalid_type():
    """Confirms error when HELCIM_JS_CONFIG is not a dictionary."""
    try:
        _validate_helcim_js_settings('invalid')
    except django_exceptions.ImproperlyConfigured as error:
        assert str(error) == 'HELCIM_JS_CONFIG setting must be a dictionary.'
    else:
        assert False

def test__validate_helcim_js_settings__missing_keys():
    """Confirms error when HELCIM_JS_CONFIG dictionary is missing keys."""
    try:
        _validate_helcim_js_settings({'example': {'missing': 'keys'}})
    except django_exceptions.ImproperlyConfigured as error:
        assert str(error) == (
            'HELCIM_JS_CONFIG values must include both a '
            '"url" and "token" key.'
        )
    else:
        assert False

@override_settings(
    HELCIM_ACCOUNT_ID=1, HELCIM_API_TOKEN=2, HELCIM_API_URL=3,
    HELCIM_TERMINAL_ID=4, HELCIM_API_TEST=5, HELCIM_JS_CONFIG={},
    HELCIM_REDACT_ALL=7, HELCIM_REDACT_CC_NAME=8, HELCIM_REDACT_CC_NUMBER=9,
    HELCIM_REDACT_CC_EXPIRY=10, HELCIM_REDACT_CC_CVV=11,
    HELCIM_REDACT_CC_TYPE=12, HELCIM_REDACT_CC_MAGNETIC=13,
    HELCIM_REDACT_CC_MAGNETIC_ENCRYPTED=14, HELCIM_REDACT_TOKEN=15,
    HELCIM_ENABLE_TRANSACTION_CAPTURE=16, HELCIM_ENABLE_TRANSACTION_REFUND=17,
    HELCIM_ENABLE_TOKEN_VAULT=18, HELCIM_ALLOW_ANONYMOUS=19,
    HELCIM_ENABLE_ADMIN=20,
)
def test__determine_helcim_settings__all_settings_provided():
    """Tests that dictionary contains all expected values."""
    helcim_settings = determine_helcim_settings()

    assert len(helcim_settings) == 20
    assert helcim_settings['account_id'] == 1
    assert helcim_settings['api_token'] == 2
    assert helcim_settings['api_url'] == 3
    assert helcim_settings['terminal_id'] == 4
    assert helcim_settings['api_test'] == 5
    assert helcim_settings['helcim_js'] == {}
    assert helcim_settings['redact_all'] == 7
    assert helcim_settings['redact_cc_name'] == 8
    assert helcim_settings['redact_cc_number'] == 9
    assert helcim_settings['redact_cc_expiry'] == 10
    assert helcim_settings['redact_cc_cvv'] == 11
    assert helcim_settings['redact_cc_type'] == 12
    assert helcim_settings['redact_cc_magnetic'] == 13
    assert helcim_settings['redact_cc_magnetic_encrypted'] == 14
    assert helcim_settings['redact_token'] == 15
    assert helcim_settings['enable_transaction_capture'] == 16
    assert helcim_settings['enable_transaction_refund'] == 17
    assert helcim_settings['enable_token_vault'] == 18
    assert helcim_settings['allow_anonymous'] == 19
    assert helcim_settings['enable_admin'] == 20

@override_settings()
def test__determine_helcim_settings__defaults():
    """Tests that defaults is provided for expected settings."""
    # Clear any settings already provided
    del settings.HELCIM_ACCOUNT_ID
    del settings.HELCIM_API_TOKEN
    del settings.HELCIM_API_URL
    del settings.HELCIM_TERMINAL_ID
    del settings.HELCIM_API_TEST
    del settings.HELICM_JS_CONFIG
    del settings.HELCIM_REDACT_ALL
    del settings.HELCIM_REDACT_CC_NAME
    del settings.HELCIM_REDACT_CC_NUMBER
    del settings.HELCIM_REDACT_CC_EXPIRY
    del settings.HELCIM_REDACT_CC_CVV
    del settings.HELCIM_REDACT_CC_TYPE
    del settings.HELCIM_REDACT_CC_MAGNETIC
    del settings.HELCIM_REDACT_CC_MAGNETIC_ENCRYPTED
    del settings.HELCIM_REDACT_TOKEN
    del settings.HELCIM_ENABLE_TRANSACTION_CAPTURE
    del settings.HELCIM_ENABLE_TRANSACTION_REFUND
    del settings.HELCIM_ENABLE_TOKEN_VAULT
    del settings.HELCIM_ALLOW_ANONYMOUS
    del settings.HELCIM_ENABLE_ADMIN

    helcim_settings = determine_helcim_settings()

    assert len(helcim_settings) == 20
    assert helcim_settings['account_id'] == ''
    assert helcim_settings['api_token'] == ''
    assert helcim_settings['api_url'] == 'https://secure.myhelcim.com/api/'
    assert helcim_settings['terminal_id'] == ''
    assert helcim_settings['api_test'] is False
    assert helcim_settings['helcim_js'] == {}
    assert helcim_settings['redact_all'] is None
    assert helcim_settings['redact_cc_name'] is True
    assert helcim_settings['redact_cc_number'] is True
    assert helcim_settings['redact_cc_expiry'] is True
    assert helcim_settings['redact_cc_cvv'] is True
    assert helcim_settings['redact_cc_type'] is True
    assert helcim_settings['redact_cc_magnetic'] is True
    assert helcim_settings['redact_cc_magnetic_encrypted'] is True
    assert helcim_settings['redact_token'] is False
    assert helcim_settings['enable_transaction_capture'] is False
    assert helcim_settings['enable_transaction_refund'] is False
    assert helcim_settings['enable_token_vault'] is False
    assert helcim_settings['allow_anonymous'] is True
    assert helcim_settings['enable_admin'] is False
