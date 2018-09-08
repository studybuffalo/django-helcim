"""Interface functions with the Helcim Commerce API.

These functions provide an agonstic interface with the Helcim Commerce
API and should work in any application (i.e. not just django-oscar).
"""

from decimal import Decimal
import logging
import requests
import xmltodict

from helcim.fields import FIELD_LIST
from helcim.exceptions import HelcimError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)

class BaseRequest(object):
    """Base class to handle validation and submission to Helcim API.

        Attributes:
            api_details (dict): Details to connect to Helcim API:

                - **url** (*str*): API URL.
                - **account_id** (*str*): Helcim account ID.
                - **token** (*str*): Helcim API token.
                - **terminal** (*str*): Helcim terminal ID.

            **kwargs (dict): Any additional transaction details.

        Keyword Args:
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
    """

    def __init__(self, api_details, **kwargs):
        self.api = api_details
        self.details = kwargs
        self.cleaned = {}

    def post(self, post_data=None):
        """Makes POST to Helcim API and provides response as dictionary.

        Args:
            post_data (dict): The parameters to pass with the POST request.

        Returns:
            dict: Helcim API response.

        Raises:
            ValueError: TBD.

        """

        LOG.debug('POST Parameters: %s', post_data)

        # Make the POST request
        try:
            response = requests.post(
                self.api['url'],
                data=post_data,
            )
        except requests.ConnectionError:
            raise HelcimError(
                'Unable to connect to Helcim API ({})'.format(self.api['url'])
            )

        # Create the dictionary ('message' is the XML structure object)
        dict_response = xmltodict.parse(response.content)['message']

        # Catch any errors in the response
        if response.status_code != 200 or dict_response['response'] == '0':
            raise HelcimError(
                'Unable to communicate with Helcim API: {}'.format(
                    dict_response['responseMessage']
                )
            )

        # Return the response
        return dict_response

    def validate_fields(self):
        """Validates Helcim API request fields and ."""

        for field_name, field_value in self.details.items():
            validation = FIELD_LIST[field_name]

            # Coerce value and any validation
            try:
                if validation.field_type == 's':
                    cleaned_value = str(field_value)

                    if validation.min and len(cleaned_value) < validation.min:
                        raise ValueError(
                            '{} field length too short.'.format(field_name)
                        )

                    if validation.max and len(cleaned_value) > validation.max:
                        raise ValueError(
                            '{} field length too long.'.format(field_name)
                        )

                elif validation.field_type == 'i':
                    cleaned_value = int(field_value)

                    if validation.min and cleaned_value < validation.min:
                        raise ValueError(
                            '{} field value too small.'.format(field_name)
                        )

                    if validation.max and cleaned_value > validation.max:
                        raise ValueError(
                            '{} field value too large.'.format(field_name)
                        )

                elif validation.field_type == 'd':
                    cleaned_value = Decimal(str(field_value))

                    if validation.min and cleaned_value < validation.min:
                        raise ValueError(
                            '{} field value too small.'.format(field_name)
                        )

                    if validation.max and cleaned_value > validation.max:
                        raise ValueError(
                            '{} field value too large.'.format(field_name)
                        )

                elif validation.field_type == 'b':
                    cleaned_value = 1 if bool(field_value) else 0

            except ValueError:
                raise ValueError

            # Check that value fits length restrictions



            # Add the field to the cleaned data
            self.cleaned[field_name] = cleaned_value

    def prepare_post_data(self, additional_data):
        """Creates POST data from object data

        Data is collected from the self.api dictionary, self.cleaned,
        and any additional_data provided.

        """
        post_data = {}

        # Convert dictionary names to the Helcim API names
        # API Data
        post_data['accountId'] = str(self.api['account_id'])
        post_data['apiToken'] = str(self.api['token'])
        post_data['terminalId'] = str(self.api['terminal'])

        # Cleaned Data
        for field_name, field_value in self.cleaned.items():
            post_data[FIELD_LIST[field_name].api_name] = str(field_value)

        # Combine with the additional data
        post_data.update(additional_data)

        return post_data

class Purchase(BaseRequest):
    """Makes a purchase request to Helcim API
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
        """Makes a purchase request"""
        self.validate_fields()
        self._determine_payment_details()

        purchase_data = self.prepare_post_data({
            'transactionType': 'purchase',
        })

        return self.post(purchase_data)

# def refund():
#     """Makes a refund request
#     """

#     pass

# def verify():
#     """Makes a verification request
#     """

#     pass

# def preauthorize():
#     """Makes a pre-authorization request
#     """

#     pass

# def capture():
#     """Makes a capture request (to complete a preauthorization)
#     """

#     pass
