"""Interface functions with the Helcim Commerce API.

These functions provide an agonstic interface with the Helcim Commerce
API and should work in any application.
"""
import requests
import xmltodict

from django.db import IntegrityError

from helcim import (
    conversions, exceptions as helcim_exceptions, mixins, models
)
from helcim.settings import SETTINGS


class BaseRequest(mixins.ResponseMixin, object):
    """Base class to handle validation and submission to Helcim API.

    Parameters:
        api_details (dict): Details to connect to Helcim API:

            - **url** (*str*): API URL.
            - **account_id** (*str*): Helcim account ID.
            - **token** (*str*): Helcim API token.
            - **terminal_id** (*str*): Helcim terminal ID.

        django_user (obj): The Django model for the requesting user.
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

    def __init__(self, api_details=None, django_user=None, **kwargs):
        self.api = self.set_api_details(api_details)
        self.details = kwargs
        self.cleaned = {}
        self.response = {}
        self.redacted_response = {}
        self.django_user = django_user

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
        if not bool(self.redacted_response):
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
    def __init__(self, save_token=False, **kwargs):
        """Extends BaseRequest to include save_token and django_user.

            Parameters:
                save_token (bool): Whether the user has requested this
                    token to be saved or not.
        """
        super(BaseCardTransaction, self).__init__(**kwargs)
        self.save_token = self._determine_save_token_status(save_token)

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
        token = self.save_token_to_vault()

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
        token = self.save_token_to_vault()

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
        token = self.save_token_to_vault()

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
        token = self.save_token_to_vault()

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

class HelcimJSResponse(mixins.ResponseMixin, object):
    """Class to handle Helcim.js Responses.

        This is a helper class that takes a Helcim.js response,
        handles any errors, converts the response into Python types
        and applies any redactions.

        Handling is more limited since all requests to the API are
        handled directly by Helcim.js. It is important to note that
        responses from Helcim.js are similar, but not identical to the
        basic Helcim API.

        Parameters:
            response (obj): the Helcim.js response POST data.
            save_token (bool): whether to save this to the
                ``django-helcim`` token vault.
            django_user (obj): a django user instance to use with
                ``django-helcim`` model instances.
    """
    def __init__(self, response, save_token=False, django_user=None):
        self.raw_response = response
        self.response = None
        self.redacted_response = None
        self.save_token = self._determine_save_token_status(save_token)
        self.django_user = django_user
        self.validated = False
        self.valid = False


    def is_valid(self):
        """Validates format is correct and notifies of any errors.

            Returns:
                boolean: True if valid without errors, otherwise false.
        """
        self.response = conversions.process_helcim_js_response(
            self.raw_response
        )

        # Updates instance to note that validation was run and record result
        self.validated = True
        self.valid = self.response['transaction_success']

        return self.valid

    def _record_response(self, transaction_type):
        """Handles saving transaction and token for various response types.

            Will run last checks to ensure data is valid before saving to
            database.

            Parameters:
                transaction_type (str): the transaction_type to save the
                    transaction as: purchase/sale (``s``), preauthorization
                    (``p``), or verification (``v``).

            Returns:
                tuple: tuple of HelcimTransaction and HelcimToken instances.
                    HelcimToken will be None if token is not saved.
        """
        if self.validated is False:
            raise helcim_exceptions.HelcimError(
                'Must validate data with the .is_valid() method '
                ' before recording purchase.'
            )

        if self.valid is False:
            raise helcim_exceptions.HelcimError(
                'Response data was invalid - cannot record purchase data.'
            )

        transaction_instance = self.save_transaction(transaction_type)
        token_instance = self.save_token_to_vault()

        return transaction_instance, token_instance

    def record_purchase(self):
        """Saves validated purchase response to database.

            Returns:
                tuple: tuple of HelcimTransaction and HelcimToken instances.
                    HelcimToken will be None if token is not saved.
        """
        return self._record_response('s')

    def record_preauthorization(self):
        """Saves validated preauthorization response to database.

            Returns:
                tuple of the HelcimTransaction and HelcimToken instances.
                    HelcimToken will be None if token is not saved.
        """
        return self._record_response('p')

    def record_verification(self):
        """Saves validated verification response to database.

            Returns:
                tuple of the HelcimTransaction and HelcimToken instances.
                    HelcimToken will be None if token is not saved.
        """
        return self._record_response('v')

def retrieve_token_details(token_id, django_user=None, customer_code=None):
    """Takes a HelcimToken ID and maps details to dictionary."""
    # Final validation to ensure token exists & belongs to proper user
    try:
        token_instance = models.HelcimToken.objects.get(
            id=token_id,
            django_user=django_user,
            customer_code=customer_code
        )
    except models.HelcimToken.DoesNotExist:
        raise helcim_exceptions.ProcessingError(
            'Unable to retrieve token details for specified customer.'
        )

    # Validation passed - map model to the dictionary
    return {
        'token': token_instance.token,
        'token_f4l4': token_instance.token_f4l4,
        'django_user': token_instance.django_user,
        'customer_code': token_instance.customer_code,
    }

def retrieve_saved_tokens(django_user=None, customer_code=None):
    """Returns list of tokens for specified customer.

        Parameters:
            django_user (obj): A Django user model instance.
            customer_code (str): A Helcim customer code.

        Returns:
            obj: A queryset of the retrieved tokens
    """
    if django_user and customer_code:
        return models.HelcimToken.objects.filter(
            django_user=django_user, customer_code=customer_code
        )

    if django_user:
        return models.HelcimToken.objects.filter(django_user=django_user)

    if customer_code:
        return models.HelcimToken.objects.filter(customer_code=customer_code)

    return models.HelcimToken.objects.none()
