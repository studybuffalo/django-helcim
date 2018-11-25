"""Interface functions with the Helcim Commerce API.

These functions provide an agonstic interface with the Helcim Commerce
API and should work in any application.
"""
from calendar import monthrange
import copy
from datetime import datetime
import re

import pytz
import requests
import xmltodict

from django.conf import settings as django_settings
from django.core import exceptions as django_exceptions
from django.db import IntegrityError

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
        self.api = self.set_api_details(api_details)
        self.details = kwargs
        self.cleaned = {}
        self.response = {}
        self.redacted_response = {}

    def _redact_api_data(self):
        """Redacts API data and updates redacted_response attribute."""
        if 'raw_request' in self.redacted_response:
            self.redacted_response['raw_request'] = re.sub(
                r'(accountId=.*?)(&|$)',
                r'accountId=REDACTED\g<2>',
                self.redacted_response['raw_request']
            )
            self.redacted_response['raw_request'] = re.sub(
                r'(apiToken=.*?)(&|$)',
                r'apiToken=REDACTED\g<2>',
                self.redacted_response['raw_request']
            )
            self.redacted_response['raw_request'] = re.sub(
                r'(terminalId=.*?)(&|$)',
                r'terminalId=REDACTED\g<2>',
                self.redacted_response['raw_request']
            )
        else:
            self.redacted_response['raw_request'] = None

    def _redact_field(self, api_name, python_name):
        """Redacts all information for the provided field.

            Method directly updates the redacted_response attribute.

            Parameters:
                api_name (str): The field name used by the Helcim API.
                python_name (str): The field name used by this
                    application.
        """
        # Redacts the raw_request data (if present)
        if self.redacted_response.get('raw_request', None):
            self.redacted_response['raw_request'] = re.sub(
                r'({}=.*?)(&|$)'.format(api_name),
                r'{}=REDACTED\g<2>'.format(api_name),
                self.redacted_response['raw_request']
            )

        # Redacts the raw_response data (if present)
        if self.redacted_response.get('raw_response', None):
            self.redacted_response['raw_response'] = re.sub(
                r'<{}>.*</{}>'.format(api_name, api_name),
                r'<{}>REDACTED</{}>'.format(api_name, api_name),
                self.redacted_response['raw_response']
            )

        if python_name in self.redacted_response:
            self.redacted_response[python_name] = None

    def set_api_details(self, details):
        """Sets the API details for this transaction.

            Will either return a dictionary of the API details from the
            provided details argument, or will look to the Django
            settings file.

            Parameters:
                details (dict): A dictionary of the API details.

            Returns:
                dict: The proper API details from the provided data.

            Raises:
                ImproperlyConfigured: A required API setting is not
                    found.
        """
        api_details = {
            'url': None,
            'account_id': None,
            'token': None,
            'terminal_id': None,
        }

        # Tries and retrieves settings form API details
        if details:
            api_details['url'] = details.get('url')
            api_details['account_id'] = details.get('account_id')
            api_details['token'] = details.get('token')
            api_details['terminal_id'] = details.get('terminal_id')

        # For any missing values, use values/defaults from settings
        if api_details['url'] is None:
            api_details['url'] = SETTINGS['api_url']

        if api_details['account_id'] is None:
            api_details['account_id'] = SETTINGS['account_id']

        if api_details['token'] is None:
            api_details['token'] = SETTINGS['api_token']

        if api_details['terminal_id'] is None:
            api_details['terminal_id'] = SETTINGS['terminal_id']

        return api_details

    def configure_test_transaction(self):
        """Adds test flag to post data if HELCIM_API_TEST is True.

            Method applies to the cleaned data (not the raw POST data).
            If the test flag is declared in both the POST data and
            Django settings file, the POST data takes precedence.
        """

        if 'test' not in self.cleaned and SETTINGS['api_test']:
            self.cleaned['test'] = SETTINGS['api_test']

    def redact_data(self):
        """Removes sensitive and identifiable data.

            By default will redact API fields and populate
            redacted_response attribute. Depending on Django settings,
            may also redact other fields.
        """
        # Copy the response data to the redacted file for updating
        self.redacted_response = copy.deepcopy(self.response)

        # Remove any API content
        self._redact_api_data()

        # Identify and redact any other specified fields
        fields = identify_redact_fields()

        for _, redact_field in fields.items():
            if redact_field['redact']:
                for field in redact_field['fields']:
                    self._redact_field(field['api'], field['python'])

    def process_error_response(self, response_message):
        """Returns error response with proper exception type.

            Parameters:
                response_message (str): The API error response message.

            Raises:
                PaymentError: Raised for any errors returned during a
                    purchase or refund transaction.
                HelcimError: Raised for any other unhandled errors.
        """
        exception_message = 'Helcim API request failed: {}'.format(
            response_message
        )

        if isinstance(self, Purchase):
            raise helcim_exceptions.PaymentError(exception_message)

        if isinstance(self, Preauthorize):
            raise helcim_exceptions.PaymentError(exception_message)

        if isinstance(self, Capture):
            raise helcim_exceptions.PaymentError(exception_message)

        if isinstance(self, Refund):
            raise helcim_exceptions.RefundError(exception_message)

        if isinstance(self, Verification):
            raise helcim_exceptions.VerificationError(exception_message)

        raise helcim_exceptions.HelcimError(exception_message)

    def convert_expiry_to_date(self, expiry):
        """Converts a 4 digit expiry to a datetime object.

            Parameters:
                expiry (str): the four digit representation of the
                    credit card expiry

            Returns:
                obj: the expiry as a datetime object.
        """

        year = int(expiry[2:])
        month = int(expiry[:2])
        day = monthrange(year, month)[1]

        return datetime(year, month, day, tzinfo=pytz.timezone('UTC')).date()

    def create_model_arguments(self, transaction_type):
        """Creates dictionary for use as transaction model arguments.

            Takes the redacted_response data and creates a dictionary
            that can be used as the keyword argumetns for the
            HelcimTransaction model.

            Parameters:
                transaction_type (str): Transaction type for this
                    transaction.

            Returns:
                dict: dictionary of the HelcimTransaction arguments.
        """
        response = self.redacted_response

        # Format the transaction_date
        if all([
                response.get('transaction_date'),
                response.get('transaction_time')
        ]):
            date_response = datetime.combine(
                response.get('transaction_date'),
                response.get('transaction_time')
            )
        else:
            date_response = None

        # Format the credit card expiry date (if present)
        if response.get('cc_expiry', None):
            cc_expiry = self.convert_expiry_to_date(
                response['cc_expiry']
            )
        else:
            cc_expiry = None

        return {
            'raw_request': response.get('raw_request'),
            'raw_response': response.get('raw_response'),
            'transaction_success': response.get('transaction_success'),
            'response_message': response.get('response_message'),
            'notice': response.get('notice'),
            'date_response': date_response,
            'transaction_type': transaction_type,
            'transaction_id': response.get('transaction_id'),
            'amount': response.get('amount'),
            'currency': response.get('currency'),
            'cc_name': response.get('cc_name'),
            'cc_number': response.get('cc_number'),
            'cc_expiry': cc_expiry,
            'cc_type': response.get('cc_type'),
            'token': response.get('token'),
            'token_f4l4': response.get('token_f4l4'),
            'avs_response': response.get('avs_response'),
            'cvv_response': response.get('cvv_response'),
            'approval_code': response.get('approval_code'),
            'order_number': response.get('order_number'),
            'customer_code': response.get('customer_code'),
        }

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
        dict_response = xmltodict.parse(response.text)['message']

        # Catch any issues with the API response
        if dict_response['response'] == '0':
            self.process_error_response(dict_response['responseMessage'])

        # Return the response
        self.response = conversions.process_api_response(
            dict_response,
            post_data,
            response.text
        )

    def save_transaction(self, transaction_type):
        """Saves provided transaction data as Django model instance.

            Parameters:
                transaction_type (str): The type of transaction (``s``
                    for purchase (sale), ``p`` for pre-authorization,
                    ``c`` for capture, and ``r`` for refund).

            Returns:
                obj: A Django model instance of the saved data.

            Raises:
                DjangoError: Issue when attempting to save transaction
                    to database.
        """
        # Redacts data if not already done
        if not self.redacted_response:
            self.redact_data()

        model_dictionary = self.create_model_arguments(transaction_type)

        try:
            saved_model = models.HelcimTransaction.objects.create(
                **model_dictionary
            )
        except IntegrityError as error:
            raise helcim_exceptions.DjangoError(
                'Unable to save transaction record: {}'.format(error)
            )
        except ValueError as error:
            raise helcim_exceptions.DjangoError(
                'Unable to save transaction record: {}'.format(error)
            )

        return saved_model

    def validate_fields(self):
        """Validates Helcim API request fields and coerces values."""
        self.cleaned = conversions.validate_request_fields(self.details)

class BaseCardTransaction(BaseRequest):
    """Base class for transactions involving credit card details."""
    def __init__(self, save_token=False, django_user=None, **kwargs):
        """Extends BaseRequest to include save_token and django_user.

            Parameters:
                save_token (bool): Whether the user has requested this
                    token to be saved or not.
                django_user (obj): The Django model for the requesting
                    user.
        """
        super(BaseCardTransaction, self).__init__(**kwargs)
        self.save_token = self._determine_save_token_status(save_token)
        self.django_user = django_user

    def _determine_save_token_status(self, user_decision):
        """Determines if Helcim card token should be saved.

            Parameters:
                user_decision (bool): Whether the user has requested to
                    save this token or not.

            Returns:
                bool: Whether a token should be saved.
        """
        # Check if vault is enabled in settings
        vault_enabled = SETTINGS['enable_token_vault']

        # If yes, check if user requested save
        if vault_enabled:
            return user_decision

        return False

    def determine_card_details(self):
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

    def save_token_to_vault(self):
        """Saves Helcim card token.

            Returns:
                obj: The HelcimToken model instance, or ``None`` (if
                    model not created).
        """
        token = self.response.get('token', None)
        token_f4l4 = self.response.get('token_f4l4', None)

        # Ensure there is a customer code (can't use token without one)
        try:
            customer_code = self.response['customer_code']
        except KeyError:
            raise helcim_exceptions.ProcessingError(
                'Unable to save token - customer code not provided'
            )

        # Ensures a django user is available if it is the identifier
        if SETTINGS['token_vault_identifier'] != 'helcim':
            if self.django_user is None:
                raise helcim_exceptions.ProcessingError(
                    'Unable to save token - user reference not provided'
                )

        if token and token_f4l4:
            token_instance, _ = models.HelcimToken.objects.get_or_create(
                token=token,
                token_f4l4=token_f4l4,
                cc_type=self.response.get('cc_type', None),
                customer_code=customer_code,
                django_user=self.django_user,
            )

            return token_instance

        return None

class Purchase(BaseCardTransaction):
    """Makes a purchase request to Helcim Commerce API."""
    def process(self):
        """Makes a purchase request.

            Returns:
                tuple: The saved HelcimTransaction model
                    instance and HelcimToken model.
        """
        self.validate_fields()
        self.configure_test_transaction()
        self.determine_card_details()

        purchase_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'purchase',
            }
        )
        self.post(purchase_data)

        purchase = self.save_transaction('s')

        if self.save_token:
            token = self.save_token_to_vault()
        else:
            token = None

        return purchase, token

class Preauthorize(BaseCardTransaction):
    """Makes a pre-authorization request to Helcim Commerce API."""
    def process(self):
        """Makes a pre-authorization request."""
        self.validate_fields()
        self.configure_test_transaction()
        self.determine_card_details()

        preauth_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'preauth',
            }
        )
        self.post(preauth_data)
        preauth = self.save_transaction('p')

        if self.save_token:
            token = self.save_token_to_vault()
        else:
            token = None

        return preauth, token

class Refund(BaseCardTransaction):
    """Makes a refund request."""
    def process(self):
        """Makes a refund request to Helcim Commerce API."""
        self.validate_fields()
        self.configure_test_transaction()
        self.determine_card_details()

        refund_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'refund',
            }
        )
        self.post(refund_data)
        refund = self.save_transaction('r')

        if self.save_token:
            token = self.save_token_to_vault()
        else:
            token = None


        return refund, token

class Verification(BaseCardTransaction):
    """Makes a verification request to Helcim Commerce API."""
    def process(self):
        """Makes a verification request to Helcim Commerce API."""
        self.validate_fields()
        self.configure_test_transaction()
        self.determine_card_details()

        verification_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'verify',
            }
        )
        self.post(verification_data)
        verification = self.save_transaction('v')

        if self.save_token:
            token = self.save_token_to_vault()
        else:
            token = None


        return verification, token

class Capture(BaseRequest):
    """Makes a capture request (to complete a preauthorization)."""
    def validate_preauth_transaction(self):
        """Confirms that a preauth transaction ID was provided.

            Raises:
                PaymentError: Error when no transaction ID provided.
        """

        if 'transaction_id' not in self.details:
            raise helcim_exceptions.PaymentError(
                'Transaction ID must be provided with capture (force) request.'
            )

    def process(self):
        """Completes a capture request."""
        self.validate_fields()
        self.validate_preauth_transaction()
        self.configure_test_transaction()

        capture_data = conversions.process_request_fields(
            self.api,
            self.cleaned,
            {
                'transactionType': 'capture',
            }
        )

        self.post(capture_data)
        capture = self.save_transaction('c')

        return capture

def identify_redact_fields():
    """Identifies which fields (if any) should be redacted.

        Configured using flags in the Django settings file.

        Returns:
            dict: A dictionary of fields to redact with corresponding
                API field and variable names.
    """
    redact_fields = {
        'name': {
            'redact': None,
            'settings': 'redact_cc_name',
            'fields': [
                {'api': 'cardHolderName', 'python': 'cc_name'},
            ]
        },
        'number': {
            'redact': None,
            'settings': 'redact_cc_number',
            'fields': [
                {'api': 'cardNumber', 'python': 'cc_number'},
            ]
        },
        'expiry': {
            'redact': None,
            'settings': 'redact_cc_expiry',
            'fields': [
                {'api': 'cardExpiry', 'python': 'cc_expiry'},
                {'api': 'expiryDate', 'python': 'cc_expiry'},
            ]
        },
        'cvv': {
            'redact': None,
            'settings': 'redact_cc_cvv',
            'fields': [
                {'api': 'cardCVV', 'python': 'cc_cvv'},
            ]
        },
        'type': {
            'redact': None,
            'settings': 'redact_cc_type',
            'fields': [
                {'api': 'cardType', 'python': 'cc_type'},
            ]
        },
        'token': {
            'redact': None,
            'settings': 'redact_token',
            'fields': [
                {'api': 'cardToken', 'python': 'token'},
                {'api': 'cardF4L4', 'python': 'token_f4l4'},
            ]
        },
        'mag': {
            'redact': None,
            'settings': 'redact_cc_magnetic',
            'fields': [
                {'api': 'cardMag', 'python': 'mag'},
            ]
        },
        'mag_enc': {
            'redact': None,
            'settings': 'redact_cc_magnetic_encrypted',
            'fields': [
                {'api': 'cardMagEnc', 'python': 'mag_enc'},
                {'api': 'serialNumber', 'python': 'mang_enc_serial_number'},
            ]
        },
    }

    # HELCIM_REDACT_ALL overrides all other settings
    if SETTINGS['redact_all'] is not None:
        if SETTINGS['redact_all'] is True:
            for key in redact_fields:
                redact_fields[key]['redact'] = True
        else:
            for key in redact_fields:
                redact_fields[key]['redact'] = False

    # Otherwise, assess each field individually
    else:
        for key, field in redact_fields.items():
            redact_fields[key]['redact'] = SETTINGS[field['settings']]

    return redact_fields

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
    token_vault_identifier = getattr(
        django_settings, 'HELCIM_TOKEN_VAULT_IDENTIFIER', 'django'
    )

    # ADMIN SETTINGS
    # -------------------------------------------------------------------------
    enable_admin = getattr(
        django_settings, 'HELCIM_ENABLE_ADMIN', False
    )

    return {
        'api_url': api_url,
        'account_id': account_id,
        'api_token': api_token,
        'terminal_id': terminal_id,
        'api_test': api_test,
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
        'token_vault_identifier': token_vault_identifier,
        'enable_admin': enable_admin,
    }

def retrieve_token_details(token_id, customer):
    """Takes a HelcimToken ID and maps details to dictionary."""
    # Final validation to ensure token exists & belongs to proper user
    try:
        # Determine what identifier is used for tokens
        customer_reference = SETTINGS['token_vault_identifier']

        if customer_reference == 'helcim':
            token_instance = models.HelcimToken.objects.get(
                id=token_id, customer_code=customer
            )
        else:
            token_instance = models.HelcimToken.objects.get(
                id=token_id, django_user=customer
            )
    except models.HelcimToken.DoesNotExist:
        raise helcim_exceptions.ProcessingError(
            'Unable to retrieve token details for specified customer.'
        )

    # Validation passed - map model to the dictionary
    return {
        'token': token_instance.token,
        'token_f4l4': token_instance.token_f4l4,
        'customer_code': token_instance.customer_code,
    }

def retrieve_saved_tokens(customer):
    """Returns list of tokens for specified customer.

        Parameters:
            customer: Either a a Django user instance or a Helcim
                customer code. The reference used is determined by the
                ``HELCIM_TOKEN_VAULT_IDENTIFIER`` setting.

        Returns:
            obj: A queryset of the retrieved tokens
    """
    if SETTINGS['token_vault_identifier'] == 'helcim':
        tokens = models.HelcimToken.objects.filter(customer_code=customer)
    else:
        tokens = models.HelcimToken.objects.filter(django_user=customer)

    return tokens

SETTINGS = determine_helcim_settings()
