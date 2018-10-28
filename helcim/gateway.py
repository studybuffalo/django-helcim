"""Interface functions with the Helcim Commerce API.

These functions provide an agonstic interface with the Helcim Commerce
API and should work in any application (i.e. not just django-oscar).
"""
import re
import requests
import xmltodict

from django.conf import settings
from django.core import exceptions as django_exceptions

from helcim import conversions, exceptions as helcim_exceptions, models


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
        self.response = {}
        self.redacted_response = {}

    def _set_api_details(self, details):
        """Sets the API details for this transaction.

        Will either return a dictionary of the API details from the
        provided details argument, or will look to the Django settings
        file.

        Parameters:
            details (dict): A dictionary of the API details.

        Returns:
            dict: The proper API details from the provided data.

        Raises:
            ImproperlyConfigured: Raised if API details cannot be
                resolved.
        """
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

    def _configure_test_transaction(self):
        """Adds test flag to post data if HELCIM_API_TEST is True.

        Method applies to the cleaned data (not the raw POST data).
        If the test flag is declared in both the POST data and Django
        settings file, the POST data takes precedence.
        """

        if 'test' not in self.cleaned and hasattr(settings, 'HELCIM_API_TEST'):
            print('add test from setting')
            self.cleaned['test'] = settings.HELCIM_API_TEST

    def _identify_redact_fields(self):
        """Identifies which fields (if any) should be redacted.

            Configured using flags in the Django settings file.

            Returns:
                dict: A dictionary of fields to redact
        """
        fields = {
            'name': False,
            'number': False,
            'expiry': False,
            'type': False,
            'token': False,
        }

        if (
                hasattr(settings, 'HELCIM_REDACT_ALL')
                and settings.HELCIM_REDACT_ALL
        ):
            fields['name'] = True
            fields['number'] = True
            fields['expiry'] = True
            fields['type'] = True
            fields['token'] = True

        if (
                hasattr(settings, 'HELCIM_REDACT_CC_NAME')
                and settings.HELCIM_REDACT_CC_NAME
        ):
            fields['name'] = True

        if (
                hasattr(settings, 'HELCIM_REDACT_CC_NUMBER')
                and settings.HELCIM_REDACT_CC_NUMBER
        ):
            fields['number'] = True

        if (
                hasattr(settings, 'HELCIM_REDACT_CC_EXPIRY')
                and settings.HELCIM_REDACT_CC_EXPIRY
        ):
            fields['expiry'] = True

        if (
                hasattr(settings, 'HELCIM_REDACT_CC_TYPE')
                and settings.HELCIM_REDACT_CC_TYPE
        ):
            fields['type'] = True

        if (
                hasattr(settings, 'HELCIM_REDACT_TOKEN')
                and settings.HELCIM_REDACT_TOKEN
        ):
            fields['token'] = True

        return fields

    def _redact_api_data(self):
        """Redacts API data and updates redacted_response attribute."""
        self.redacted_response['raw_request'] = re.sub(
            r'(accountId=.+?)(&|$)',
            r'accountId=REDACTED\g<2>',
            self.redacted_response['raw_request']
        )
        self.redacted_response['raw_request'] = re.sub(
            r'(apiToken=.+?)(&|$)',
            r'apiToken=REDACTED\g<2>',
            self.redacted_response['raw_request']
        )
        self.redacted_response['raw_request'] = re.sub(
            r'(terminalId=.+?)(&|$)',
            r'terminalId=REDACTED\g<2>',
            self.redacted_response['raw_request']
        )

    def _redact_field(self, api_name, python_name):
        """Redacts all information for the provided field.

            Method directly updates the redacted_response attribute.

            Parameters:
                api_name (str): The field name used by the Helcim API.
                python_name (str): The field name used by this
                    application.
        """
        # Redacts the raw_request data
        self.redacted_response['raw_request'] = re.sub(
            r'({}=.+?)(&|$)'.format(api_name),
            r'{}=REDACTED\g<2>'.format(api_name),
            self.redacted_response['raw_request']
        )

        # Redacts the raw_response data
        self.redacted_response['raw_response'] = re.sub(
            r'<{}>.*</{}>'.format(api_name, api_name),
            r'<{}>REDACTED</{}>'.format(api_name, api_name),
            self.redacted_response['raw_response']
        )

        if python_name in self.redacted_response:
            self.redacted_response[python_name] = None

    def _redact_data(self):
        """Removes sensitive and identifiable data.

        By default will redact API fields and populate
        redacted_response attribute. Depending on Django settings, may
        also redact other fields.
        """
        # Copy the response data to the redacted file for updating
        self.redacted_response = self.response

        # Remove any API content
        self._redact_api_data()

        # Remove any other redacted data (as needed)
        fields = self._identify_redact_fields()

        if fields['name']:
            self._redact_field('cardHolderName', 'cc_name')

        if fields['number']:
            self._redact_field('cardNumber', 'cc_number')

        if fields['expiry']:
            self._redact_field('expiryDate', 'cc_expiry')

        if fields['type']:
            self._redact_field('cardType', 'cc_type')

        if fields['token']:
            self._redact_field('cardToken', 'token')

    def process_error_response(self, response_message):
        """Returns error response with proper exception type.

            Parameters:
                response_message (str): The API error response message.

            Raises:
                PaymentError: Raised for any errors returned during a
                    purchase transaction.
                HelcimError: Raised for any other unhandled errors.
        """
        exception_message = 'Helcim API request failed: {}'.format(
            response_message
        )

        if isinstance(self, Purchase):
            raise helcim_exceptions.PaymentError(exception_message)

        raise helcim_exceptions.HelcimError(exception_message)

    def post(self, post_data=None):
        """Makes POST to Helcim API and updates response attribute.

        Parameters:
            post_data (dict): The parameters to pass with the POST request.

        Raises:
            ProcessingError: An error occurred connecting or
                communicating with Helcim API.
        """
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
        self.response = conversions.process_api_response(
            dict_response,
            post_data,
            response.content
        )

    def save_transaction(self, transaction_type):
        """Saves provided transaction data as Django model instance.

            Parameters:
                transaction_type (str): The type of transaction (`s`
                    for purchase (sale), `p` for pre-authorization,
                    `c` for capture, and `r` for refund).

            Returns:
                obj: A Django model instance of the saved data.
        """
        self._redact_data()

        saved_model = models.HelcimTransaction.objects.create(
            raw_request=self.redacted_response['raw_request'],
            raw_response=self.redacted_response['raw_response'],
            transaction_type=transaction_type
        )

        return saved_model

    def validate_fields(self):
        """Validates Helcim API request fields and coerces values."""
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
        self._configure_test_transaction()
        self._determine_payment_details()

        purchase_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'purchase',
            }
        )

        self.post(purchase_data)
        purchase = self.save_transaction('s')

        return purchase

class Preauthorize(BaseRequest):
    """Makes a pre-authorization request.
    """

class Capture(BaseRequest):
    """Makes a capture request (to complete a preauthorization).
    """

class Refund(BaseRequest):
    """Makes a refund request.
    """
class Verification(BaseRequest):
    """Makes a verification request.
    """
