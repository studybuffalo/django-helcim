"""Determines relevant settings for django-helcim functioning."""
from django.conf import settings as django_settings
from django.core import exceptions as django_exceptions

def _validate_helcim_js_settings(helcim_js):
    """Confirms that declared Helcim.js are in proper format."""
    if isinstance(helcim_js, dict) is False:
        message = 'HELCIM_JS_CONFIG setting must be a dictionary.'
        raise django_exceptions.ImproperlyConfigured(message)

    for _, value in helcim_js.items():
        if 'url' not in value or 'token' not in value:
            message = (
                'HELCIM_JS_CONFIG values must include both a '
                '"url" and "token" key.'
            )
            raise django_exceptions.ImproperlyConfigured(message)

def determine_helcim_settings():
    """Collects all possible django-helcim settings for easy use.

        Performs basic validation of required settings and assigns
        defaults where applicable.

        Returns:
            dict: Summary of all possible django-helcim settings.
    """
    # API SETTINGS
    # -------------------------------------------------------------------------
    # Required settings
    try:
        account_id = getattr(django_settings, 'HELCIM_ACCOUNT_ID')
    except AttributeError:
        raise django_exceptions.ImproperlyConfigured(
            'You must define a HELCIM_ACCOUNT_ID setting'
        )

    try:
        api_token = getattr(django_settings, 'HELCIM_API_TOKEN')
    except AttributeError:
        raise django_exceptions.ImproperlyConfigured(
            'You must define a HELCIM_API_TOKEN setting'
        )

    # Other settings
    api_url = getattr(
        django_settings, 'HELCIM_API_URL', 'https://secure.myhelcim.com/api/'
    )
    terminal_id = getattr(django_settings, 'HELCIM_TERMINAL_ID', '')
    api_test = getattr(django_settings, 'HELCIM_API_TEST', None)

    # HELCIM.JS SETTINGS
    # -------------------------------------------------------------------------
    helcim_js = getattr(django_settings, 'HELCIM_JS_CONFIG', {})
    _validate_helcim_js_settings(helcim_js)

    # REDACTION SETTINGS
    # -------------------------------------------------------------------------
    redact_all = getattr(django_settings, 'HELCIM_REDACT_ALL', None)
    redact_cc_name = getattr(django_settings, 'HELCIM_REDACT_CC_NAME', True)
    redact_cc_number = getattr(
        django_settings, 'HELCIM_REDACT_CC_NUMBER', True
    )
    redact_cc_expiry = getattr(
        django_settings, 'HELCIM_REDACT_CC_EXPIRY', True
    )
    redact_cc_cvv = getattr(django_settings, 'HELCIM_REDACT_CC_CVV', True)
    redact_cc_type = getattr(django_settings, 'HELCIM_REDACT_CC_TYPE', True)
    redact_cc_magnetic = getattr(
        django_settings, 'HELCIM_REDACT_CC_MAGNETIC', True
    )
    redact_cc_magnetic_encrypted = getattr(
        django_settings, 'HELCIM_REDACT_CC_MAGNETIC_ENCRYPTED', True
    )
    redact_token = getattr(django_settings, 'HELCIM_REDACT_TOKEN', False)

    # TRANSACTION FUNCTIONALITY SETTINGS
    # -------------------------------------------------------------------------
    enable_transaction_capture = getattr(
        django_settings, 'HELCIM_ENABLE_TRANSACTION_CAPTURE', False
    )
    enable_transaction_refund = getattr(
        django_settings, 'HELCIM_ENABLE_TRANSACTION_REFUND', False
    )

    # TOKEN VAULT SETTINGS
    # -------------------------------------------------------------------------
    enable_token_vault = getattr(
        django_settings, 'HELCIM_ENABLE_TOKEN_VAULT', False
    )

    # ADMIN SETTINGS
    # -------------------------------------------------------------------------
    enable_admin = getattr(
        django_settings, 'HELCIM_ENABLE_ADMIN', False
    )

    # OTHER SETTINGS
    # -------------------------------------------------------------------------
    allow_anonymous = getattr(
        django_settings, 'HELCIM_ALLOW_ANONYMOUS', True
    )

    return {
        'api_url': api_url,
        'account_id': account_id,
        'api_token': api_token,
        'terminal_id': terminal_id,
        'api_test': api_test,
        'helcim_js': helcim_js,
        'redact_all': redact_all,
        'redact_cc_name': redact_cc_name,
        'redact_cc_number': redact_cc_number,
        'redact_cc_expiry': redact_cc_expiry,
        'redact_cc_cvv': redact_cc_cvv,
        'redact_cc_type': redact_cc_type,
        'redact_cc_magnetic': redact_cc_magnetic,
        'redact_cc_magnetic_encrypted': redact_cc_magnetic_encrypted,
        'redact_token': redact_token,
        'enable_transaction_capture': enable_transaction_capture,
        'enable_transaction_refund': enable_transaction_refund,
        'enable_token_vault': enable_token_vault,
        'enable_admin': enable_admin,
        'allow_anonymous': allow_anonymous,
    }

SETTINGS = determine_helcim_settings()
