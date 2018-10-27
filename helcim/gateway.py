"""Interface functions with the Helcim Commerce API.

These functions provide an agonstic interface with the Helcim Commerce
API and should work in any application (i.e. not just django-oscar).
"""

import requests
import xmltodict

from django.conf import settings
from django.core import exceptions as django_exceptions

from helcim import conversions
from helcim import exceptions as helcim_exceptions


class BaseRequest():
    """Base class to handle validation and submission to Helcim API.

    Parameters:
        api_details (dict): Details to connect to Helcim API:

            - **url** (*str*): API URL.
            - **account_id** (*str*): Helcim account ID.
            - **token** (*str*): Helcim API token.
            - **terminal_id** (*str*): Helcim terminal ID.

        **kwargs (dict): Any additional transaction details.

    Keyword Arguments:
        amount (dec, optional): The amount for the transaction.
        currency (str, optional): The currency for the transaction.
        cc_name (str, optional): Name of the credit cardholder.
        cc_number (str, optional): 16 digit credit card number.
        cc_expiry (str, optional): 4 digit (MMYY) credit card
            expiry.
        cc_cvv (str, optional): 3 or 4 digit credit card CVV.
        cc_address (str, optional): Address of the credit
            cardholder.
        cc_postal_code (str, optional): Postal code/zip code of
            the credit cardholder.
        customer_code (str, optional): Helcim customer code.
        token (str, optional): 23 digit Helcim card token.
        token_f4l4 (str, optional): 8 digit "first four digits and
            last four digits" of the credit card number
        token_f4l4_skip (bool, optional): Whether to skip the F4L4
            verification.
        mag (string, optional): Non-encrypted credit card magnetic
            strip data.
        mag_enc (str, optional): Encrypted credit card magnestic
            strip data.
        mag_enc_serial_number (string, optional): Terminal serial
            number.
        order_number (str, optional): An assigned order number for
            the purchase.
        ecommerce (bool, optional): Whether this is an e-commerce
            transaction or not.
        comments (str, optional): Any additional comments with this
            transaction.
        billing_contact_name (str, optional): Billing address
            contact name.
        billing_business_name (str, optional): Billing address
            business name.
        billing_street_1 (str, optional): Billing street address
            (line 1).
        billing_street_2 (str, optional): Billing street address
            (line 2).
        billing_city (str, optional): Billing city.
        billing_province (str, optional): Billing province.
        billing_country (str, optional): Billing country.
        billing_postal_code (str, optional): Billing postal code.
        billing_phone (str, optional): Billing phone number.
        billing_fax (str, optional): Billing fax number
        billing_email (str, optional): Billing email.
        shipping_contact_name (str, optional): Shipping contact
                name.
        shipping_business_name (str, optional): Shipping business
            name.
        shipping_street_1 (str, optional): Shipping street address
            (line 1).
        shipping_street_2 (str, optional): Shipping street address
            (line 2).
        shipping_city (str, optional): Shipping city.
        shipping_province (str, optional): Shipping province.
        shipping_country (str, optional): Shipping country.
        shipping_postal_code (str, optional): Shipping postal code.
        shipping_phone (str, optional): Shipping phone number.
        shipping_fax (str, optional): Shipping fax number.
        shipping_email (str, optional): Shipping email address.
        amount_shipping (dec, optional): Shipping cost.
        amount_tax (dec, optional): Tax amount.
        shipping_method (str, optional): Method of shipping.
        tax_details (str, optional): Name for the tax (e.g. GST).
        test (bool, optional): Whether this is a test transaction or not.
    """

    def __init__(self, api_details=None, **kwargs):
        self.api = self._set_api_details(api_details)
        self.details = kwargs
        self.cleaned = {}

    def _set_api_details(self, details):
        """Sets the API details for this transaction."""
        # Provided API details override ones in the settings
        if details:
            url = details['url']
            account_id = details['account_id']
            token = details['token']
            terminal_id = details['terminal_id']
        # Default uses details from the settings files
        else:
            setting_names = [
                'HELCIM_API_URL',
                'HELCIM_ACCOUNT_ID',
                'HELCIM_API_TOKEN',
                'HELCIM_TERMINAL_ID',
            ]

            # Confirm all required settings are entered
            for setting_name in setting_names:
                if not hasattr(settings, setting_name):
                    raise django_exceptions.ImproperlyConfigured(
                        'You must define a {} setting'.format(setting_name)
                    )

            url = settings.HELCIM_API_URL
            account_id = settings.HELCIM_ACCOUNT_ID
            token = settings.HELCIM_API_TOKEN
            terminal_id = settings.HELCIM_TERMINAL_ID

        return {
            'url': url,
            'account_id': account_id,
            'token': token,
            'terminal_id': terminal_id,
        }

    def _configure_test_transaction(self, post_data):
        """Makes this a test transaction if specified in settings."""
        # Test flag in post_data takes precedence
        if post_data:
            if all([
                    not 'test' in post_data,
                    hasattr(settings, 'HELCIM_API_TEST')
            ]):
                post_data['test'] = settings.HELCIM_API_TEST
        else:
            if hasattr(settings, 'HELCIM_API_TEST'):
                post_data = {'test': settings.HELCIM_API_TEST}

        return post_data

    def process_error_response(self, response_message):
        """Returns error response with proper exception type."""
        exception_message = 'Helcim API request failed: {}'.format(
            response_message
        )

        if isinstance(self, Purchase):
            raise helcim_exceptions.PaymentError(exception_message)

        raise helcim_exceptions.HelcimError(exception_message)

    def post(self, post_data=None):
        """Makes POST to Helcim API and returns response.

        Parameters:
            post_data (dict): The parameters to pass with the POST request.

        Returns:
            dict: Processed Helcim API response.

        Raises:
            ProcessingError: An error occurred connecting or
                communicating with Helcim API.
        """

        post_data = self._configure_test_transaction(post_data)

        # Make the POST request
        try:
            response = requests.post(
                self.api['url'],
                data=post_data,
            )
        except requests.ConnectionError:
            raise helcim_exceptions.ProcessingError(
                'Unable to connect to Helcim API ({})'.format(self.api['url'])
            )

        # Catch any response errors in status code
        if response.status_code != 200:
            raise helcim_exceptions.ProcessingError(
                'Helcim API request failed with status code {}'.format(
                    response.status_code
                )
            )

        # Create the dictionary ('message' is the XML structure object)
        dict_response = xmltodict.parse(response.content)['message']

        # Catch any issues with the API response
        if dict_response['response'] == '0':
            self.process_error_response(dict_response['responseMessage'])

        # Return the response
        return conversions.process_api_response(
            dict_response,
            post_data,
            response.content
        )

    def validate_fields(self):
        """Validates Helcim API request fields and ."""
        self.cleaned = conversions.validate_request_fields(self.details)

class Purchase(BaseRequest):
    """Makes a purchase request to Helcim API.
    """

    def _determine_payment_details(self):
        """Confirms valid payment details and updates self.cleaned.

        Cycles through the provided details to determine the most
        appropriate payment method. If multiple methods provided, only the
        first match is returned (token > customer code > CC number >
        encrypted magnetic strip > magnetic strip).

        Raises:
            ValueError: No valid payment details provided.
        """

        payment_fields = [
            'token', 'customer_code', 'token_f4l4', 'token_f4l4_skip',
            'cc_number', 'cc_expiry', 'cc_name', 'cc_cvv', 'cc_address',
            'cc_postal_code', 'mag_enc', 'mag_enc_serial_number', 'mag'
        ]

        if 'token' in self.cleaned and 'customer_code' in self.cleaned:
            # F4L4 required or it must be explicitly skipped
            f4l4_skip = self.cleaned.get('token_f4l4_skip', False)

            if f4l4_skip:
                payment_fields.remove('token')
                payment_fields.remove('customer_code')
                payment_fields.remove('token_f4l4_skip')

            if 'token_f4l4' in self.cleaned:
                payment_fields.remove('token')
                payment_fields.remove('customer_code')
                payment_fields.remove('token_f4l4')

        elif 'customer_code' in self.cleaned:
            payment_fields.remove('customer_code')

        elif 'cc_number' in self.cleaned and 'cc_expiry' in self.cleaned:
            payment_fields.remove('cc_number')
            payment_fields.remove('cc_expiry')

            # Add any additional CC details (as provided)
            if 'cc_name' in self.cleaned:
                payment_fields.remove('cc_name')

            if 'cc_cvv' in self.cleaned:
                payment_fields.remove('cc_cvv')

            if 'cc_address' in self.cleaned:
                payment_fields.remove('cc_address')

            if 'cc_postal_code' in self.cleaned:
                payment_fields.remove('cc_postal_code')

        elif (
                'mag_enc' in self.cleaned
                and 'mag_enc_serial_number' in self.cleaned
        ):
            payment_fields.remove('mag_enc')
            payment_fields.remove('mag_enc_serial_number')

        elif 'mag' in self.cleaned:
            payment_fields.remove('mag')

        # Raise error if no fields have been removed
        if len(payment_fields) == 13:
            raise ValueError('No valid payment details provided.')

        # Remove any other fields from self.cleaned
        for field in payment_fields:
            self.cleaned.pop(field, None)

    def process(self):
        """Makes a purchase request."""
        self.validate_fields()
        self._determine_payment_details()

        purchase_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'purchase',
            }
        )

        return self.post(purchase_data)

def refund():
    """Makes a refund request.
    """

    pass

def verify():
    """Makes a verification request.
    """

    pass

def preauthorize():
    """Makes a pre-authorization request.
    """

    pass

def capture():
    """Makes a capture request (to complete a preauthorization).
    """

    pass
