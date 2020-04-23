"""Mixins to help support Helcim API interactions."""
from calendar import monthrange
import copy
from datetime import datetime
import re

import pytz

from django.db import IntegrityError

from helcim import exceptions as helcim_exceptions
from helcim.settings import SETTINGS
from helcim.models import HelcimToken, HelcimTransaction


class ResponseMixin():
    """Methods to support handling a Helcim repsonse.

        Handles some data manipulations to prepare for saving to a
        model instance and applies relevant redactions to data.
     """
    @classmethod
    def _identify_redact_fields(cls):
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
                    {'api': 'serialNumber', 'python': 'mang_enc_serial_number'}, # pylint: disable=line-too-long
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

    @classmethod
    def _convert_expiry_to_date(cls, expiry):
        """Converts a 4 digit expiry to a datetime object.

            Parameters:
                expiry (str): the four digit representation of the
                    credit card expiry

            Returns:
                obj: the expiry as a datetime object.
        """

        year = 2000 + int(expiry[2:])
        month = int(expiry[:2])
        day = monthrange(year, month)[1]

        return datetime(year, month, day, tzinfo=pytz.timezone('UTC')).date()

    @classmethod
    def _determine_save_token_status(cls, user_decision):
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

    def _determine_user_reference(self):
        """Validates and returns appropriate user reference.

            Determines if an absent or anonymous user is permitted.
            Returns an exception if they are provided and not allowed.
        """
        # Handles anonymous/no user situations
        if SETTINGS['allow_anonymous']:
            if self.django_user is None or self.django_user.is_anonymous:
                return None
        else:
            if self.django_user is None or self.django_user.is_anonymous:
                raise helcim_exceptions.ProcessingError(
                    'Required Django user reference not provided.'
                )

        # Otherwise can just return the provided user model
        return self.django_user

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
                r'<{0}>.*</{0}>'.format(api_name),
                r'<{0}>REDACTED</{0}>'.format(api_name),
                self.redacted_response['raw_response']
            )

        if python_name in self.redacted_response:
            self.redacted_response[python_name] = None

    def redact_data(self):
        """Removes sensitive and identifiable data.

            By default will redact API fields and populate
            redacted_response attribute. Depending on Django settings,
            may also redact other fields in the formated and raw
            response.
        """
        # Copy the response data to the redacted file for updating
        self.redacted_response = copy.deepcopy(self.response)

        # Remove any API content
        self._redact_api_data()

        # Identify and redact any other specified fields
        fields = self._identify_redact_fields()

        for _, redact_field in fields.items():
            if redact_field['redact']:
                for field in redact_field['fields']:
                    self._redact_field(field['api'], field['python'])

        if fields['name']['redact']:
            self.response['cc_name'] = None

        if fields['expiry']['redact']:
            self.response['cc_expiry'] = None

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
            cc_expiry = self._convert_expiry_to_date(
                response['cc_expiry']
            )
        else:
            cc_expiry = None

        # Return proper user reference
        django_user = self._determine_user_reference()

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
            'django_user': django_user,
        }

    def save_transaction(self, transaction_type):
        """Saves HelcimTransaction with redacted response details."""
        # Redacts data if not already done
        if not self.redacted_response:
            self.redact_data()

        model_dictionary = self.create_model_arguments(transaction_type)

        try:
            transaction_instance = HelcimTransaction.objects.create(
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

        return transaction_instance

    def save_token_to_vault(self):
        """Saves Helcim card token.

            Returns:
                obj: The HelcimToken model instance, or ``None`` (if
                    model not created).
        """
        # Confirms that the token should be saved
        if self.save_token is False:
            return None

        token = self.response.get('token', None)
        token_f4l4 = self.response.get('token_f4l4', None)
        cc_name = self.response.get('cc_name', None)
        raw_expiry = self.response.get('cc_expiry', None)
        cc_expiry = (
            self._convert_expiry_to_date(raw_expiry) if raw_expiry else None
        )

        # Ensure there is a customer code (can't use token without one)
        try:
            customer_code = self.response['customer_code']
        except KeyError:
            raise helcim_exceptions.ProcessingError(
                'Unable to save token - customer code not provided'
            )

        # Retrieve proper user reference
        django_user = self._determine_user_reference()

        if token and token_f4l4:
            token_instance, _ = HelcimToken.objects.get_or_create(
                token=token,
                token_f4l4=token_f4l4,
                cc_name=cc_name,
                cc_expiry=cc_expiry,
                cc_type=self.response.get('cc_type', None),
                customer_code=customer_code,
                django_user=django_user,
            )

            return token_instance

        # If unable to save token, return None
        return None

class HelcimJSMixin():
    """Provides Helcim.js URL and token details in the view context.

        This is a helper mixin that allows you to declare your Helcim.js
        configuration details within your Django settings. They are then
        injected into the view context to allow you to easily declare
        them within a template.
    """
    def get_context_data(self, **kwargs):
        """Overrides the view method to add Helcim.js details."""
        # Retrieve existing context
        context = super().get_context_data(**kwargs)

        # Add the Helcim.js configuration details
        context['helcim_js'] = SETTINGS['helcim_js']

        # Add a helper "test" input to allow declaration of test status
        # This input flags a transaction as a test and allows testing
        # in environments without SSL enabled (e.g. the Django
        # development server)
        for config in context['helcim_js']:
            if context['helcim_js'][config].get('test', False):
                test_input = '<input id="test" type="hidden" value="1">'
            else:
                test_input = ''

            context['helcim_js'][config]['test_input'] = test_input

        return context
