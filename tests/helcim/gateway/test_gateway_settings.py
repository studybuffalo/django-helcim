"""Tests for the determine_helcim_settings function."""
from django.conf import settings
from django.core import exceptions as django_exceptions
from django.test import override_settings

from helcim.gateway import determine_helcim_settings

@override_settings(
    HELCIM_ACCOUNT_ID=1, HELCIM_API_TOKEN=2, HELCIM_API_URL=3,
    HELCIM_TERMINAL_ID=4, HELCIM_API_TEST=5, HELCIM_REDACT_ALL=6,
    HELCIM_REDACT_CC_NAME=7, HELCIM_REDACT_CC_NUMBER=8,
    HELCIM_REDACT_CC_EXPIRY=9, HELCIM_REDACT_CC_CVV=10,
    HELCIM_REDACT_CC_TYPE=11, HELCIM_REDACT_CC_MAGNETIC=12,
    HELCIM_REDACT_CC_MAGNETIC_ENCRYPTED=13, HELCIM_REDACT_TOKEN=14,
    HELCIM_ENABLE_TRANSACTION_CAPTURE=15, HELCIM_ENABLE_TRANSACTION_REFUND=16,
    HELCIM_ENABLE_TOKEN_VAULT=17, HELCIM_ALLOW_ANONYMOUS=18,
    HELCIM_ENABLE_ADMIN=19,
)
def test_determine_helcim_settings_all_settings_provided():
    """Tests that dictionary contains all expected values."""
    helcim_settings = determine_helcim_settings()

    assert len(helcim_settings) == 19
    assert helcim_settings['account_id'] == 1
    assert helcim_settings['api_token'] == 2
    assert helcim_settings['api_url'] == 3
    assert helcim_settings['terminal_id'] == 4
    assert helcim_settings['api_test'] == 5
    assert helcim_settings['redact_all'] == 6
    assert helcim_settings['redact_cc_name'] == 7
    assert helcim_settings['redact_cc_number'] == 8
    assert helcim_settings['redact_cc_expiry'] == 9
    assert helcim_settings['redact_cc_cvv'] == 10
    assert helcim_settings['redact_cc_type'] == 11
    assert helcim_settings['redact_cc_magnetic'] == 12
    assert helcim_settings['redact_cc_magnetic_encrypted'] == 13
    assert helcim_settings['redact_token'] == 14
    assert helcim_settings['enable_transaction_capture'] == 15
    assert helcim_settings['enable_transaction_refund'] == 16
    assert helcim_settings['enable_token_vault'] == 17
    assert helcim_settings['allow_anonymous'] == 18
    assert helcim_settings['enable_admin'] == 19

@override_settings()
def test_determine_helcim_settings_missing_account_id():
    """Tests that error is generated with account ID is missing."""
    del settings.HELCIM_ACCOUNT_ID

    try:
        determine_helcim_settings()
    except django_exceptions.ImproperlyConfigured as error:
        assert str(error) == 'You must define a HELCIM_ACCOUNT_ID setting'
    else:
        assert False

@override_settings()
def test_determine_helcim_settings_missing_api_token():
    """Tests that error is generated with API token is missing."""
    del settings.HELCIM_API_TOKEN

    try:
        determine_helcim_settings()
    except django_exceptions.ImproperlyConfigured as error:
        assert str(error) == 'You must define a HELCIM_API_TOKEN setting'
    else:
        assert False

@override_settings()
def test_determine_helcim_settings_defaults():
    """Tests that defaults is provided for expected settings."""
    # Clear any settings already provided
    del settings.HELCIM_API_URL
    del settings.HELCIM_TERMINAL_ID
    del settings.HELCIM_API_TEST
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

    assert len(helcim_settings) == 19
    assert helcim_settings['api_url'] == 'https://secure.myhelcim.com/api/'
    assert helcim_settings['terminal_id'] == ''
    assert helcim_settings['api_test'] is None
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
