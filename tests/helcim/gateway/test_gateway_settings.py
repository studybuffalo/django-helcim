"""Tests for the determine_helcim_settings function."""
from django.conf import settings
from django.test import override_settings


# TODO: Move this into the settings module
# @override_settings()
# def test_determine_save_token_status_not_specified():
#     del settings.HELCIM_ENABLE_TOKEN_VAULT
#     details = {
#         'token': 'abcdefghijklmnopqrstuvw',
#         'customer_code': 'CST1000',
#         'token_f4l4': '11119999',
#     }

#     transaction = gateway.BaseCardTransaction(
#         api_details=API_DETAILS, **details
#     )
#     status = transaction._determine_save_token_status(True)

#     assert status is False


# TODO: Move this into a new test for setting generations
# @override_settings()
# def test_set_api_details_no_account_id():
#     del settings.HELCIM_ACCOUNT_ID

#     try:
#         gateway.BaseRequest()
#     except django_exceptions.ImproperlyConfigured as error:
#         assert True
#         assert str(error) == 'You must define a HELCIM_ACCOUNT_ID setting'
#     else:
#         assert False

# @override_settings()
# def test_set_api_details_no_api_token():
#     del settings.HELCIM_API_TOKEN

#     try:
#         gateway.BaseRequest()
#     except django_exceptions.ImproperlyConfigured as error:
#         assert True
#         assert str(error) == 'You must define a HELCIM_API_TOKEN setting'
#     else:
#         assert False

# @override_settings()
# def test_set_api_details_none():
#     del settings.HELCIM_API_URL
#     del settings.HELCIM_ACCOUNT_ID
#     del settings.HELCIM_API_TOKEN
#     del settings.HELCIM_TERMINAL_ID

#     try:
#         gateway.BaseRequest()
#     except django_exceptions.ImproperlyConfigured:
#         assert True
#     else:
#         assert False

# @override_settings()
# def test_configure_test_transaction_not_set():
#     del settings.HELCIM_API_TEST
#     base = gateway.BaseRequest(api_details=API_DETAILS)

#     base.configure_test_transaction()

#     assert 'test' not in base.cleaned
