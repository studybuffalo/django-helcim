"""Interface functions with the Helcim Commerce API.

These functions provide a interface with the Helcim Commerce API.
These functions are agnostic and should work in any applications (i.e.
not just django-oscar).
"""
from decimal import Decimal
import requests
import xmltodict

from .fields import FIELD_LIST

class BaseRequest(object):
    """Base class to handle validation and submission to Helcim API.

        Attributes:
            api_details (dict): Details to connect to Helcim API:

                - url (str): API URL.
                - account_id (str): Helcim account ID.
                - token (str): Helcim API token.
                - terminal (str): Helcim terminal ID.

            **kwargs (dict): All transaction details.

        Keyword Args:
            amount (dec): The amount being purchased.
            currency (str): The currency of the transaction.
            cc_name (str): Name of the credit cardholder.
            cc_number (int): 16 digit credit card number.
            cc_expiry (int): 4 digit (MMYY) credit card expiry.
            cc_cvv (int): 3 digit credit card CVV.
            cc_address (str): Address of the credit cardholder.
            cc_postal_code (str): Postal code/zip code of the credit
                cardholder.
            customer_code (str): Helcim customer code.
            token (str): 23 digit Helcim card token.
            token_f4l4 (int): 8 digit "first four digits and last four
                digits" of the credit card number
            token_f4l4_skip (bool): Whether to skip the F4L4
                verification.
            mag (string): Non-encrypted credit card magnetic strip
                data.
            mag_enc (str): Encrypted credit card magnestic strip
                data.
            mag_enc_serial_number (string): Terminal serial number.
            order_number (str, optional): An assigned order number for the
                purchase.
            ecommerce (bool, optional): Whether this is an e-commerce
                transaction or not.
            comments (str, optional): Any additional comments with this
                transaction.
            billing_contact_name (str, optional): Billing address contact
                name.
            billing_business_name (str, optional): Billing address
                business name.
            billing_street_1 (str, optional): Billing street address.
            billing_street_2 (str, optional): Billing street address.
            billing_city (str, optional): Billing city.
            billing_province (str, optional): Billing province.
            billing_country (str, optional): Billing country.
            billing_postal_code (str, optional): Billing postal code.
            billing_phone (str, optional): Billing phone number.
            billing_fax (str, optional): Billing fax number
            billing_email (str, optional): Billing email.
            shipping_contact_name (str, optional): Shipping contact name.
            shipping_business_name (str, optional): Shipping business name.
            shipping_street_1 (str, optional): Shipping street address.
            shipping_street_2 (str, optional): Shipping street address.
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
            tax_details (str, optional): Tax name.
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

        # Setup the POST header
        post_headers = {'content-type': 'text/plain; charset=utf-8'}

        # Make the POST request
        response = requests.post(
            self.api['url'],
            post_data,
            headers=post_headers
        )

        # Error handling

        # Return the response
        return xmltodict.parse(response)

    def validate_fields(self):
        """Validates Helcim API request fields."""

        for field_name, field_value in self.details.items():
            validation = FIELD_LIST[field_name]

            # Check that value can be coerced
            try:
                if validation.field_type == 's':
                    cleaned_value = str(field_value)
                elif validation.field_type == 'i':
                    cleaned_value = int(field_value)
                elif validation.field_type == 'd':
                    cleaned_value = Decimal(field_value)
                elif validation.field_type == 'b':
                    cleaned_value = bool(field_value)
            except ValueError:
                raise ValueError

            # Check that value fits length restrictions
            if validation.min and len(cleaned_value) < validation.min:
                raise ValueError

            if validation.max and len(cleaned_value) < validation.max:
                raise ValueError

            # Add the field to the cleaned data
            self.cleaned[field_name] = cleaned_value

class Purchase(BaseRequest):
    """Makes a purchase request to Helcim API
    """

    def _determine_payment_details(self):
        """Returns most appropriate payment details for Helcim API request.

        Cycles through the provided details to determine the most
        appropriate payment method. If multiple methods provided, only the
        first match is returned (token > customer code > CC number >
        encrypted magnetic strip > magnetic strip).

        Returns:
            dict: Dictionary of the appropriate payment details.
        Raises:
            ValueError: No valid payment details provided.
        """

        if 'token' in self.details and 'customer_code' in self.details:
            # F4L4 required or it must be explicitly skipped
            f4l4_skip = self.details.get('token_f4l4_skip', False)

            if f4l4_skip:
                return {
                    'cardToken': self.details['token'],
                    'customerCode': self.details['customer_code'],
                    'cardF4L4Skip': 1,
                }

            if 'token_f4l4' in self.details:
                return {
                    'cardToken': self.details['token'],
                    'customerCode': self.details['customer_code'],
                    'cardF4L4': self.details['token_f4l4'],
                }

        elif 'customer_code' in self.details:
            return {
                'customerCode': self.details['customer_code']
            }

        elif 'cc_number' in self.details and 'cc_expiry' in self.details:
            cc_details = {
                'cardNumber': self.details['cc_number'],
                'cardexpiry': self.details['cc_expiry'],
            }

            # Add any additional CC details (as provided)
            if 'cc_name' in self.details:
                cc_details.update(
                    {'cardHolderName': self.details['cc_name']}
                )

            if 'cc_cvv' in self.details:
                cc_details.update(
                    {'cardCVV': self.details['cc_cvv']}
                )

            if 'cc_address' in self.details:
                cc_details.update(
                    {'cardHolderAddress': self.details['cc_address']}
                )

            if 'cc_postal_code' in self.details:
                cc_details.update(
                    {'cardHolderPostalCode': self.details['cc_postal_code']}
                )

            return cc_details

        elif (
                'mag_enc' in self.details
                and 'mag_enc_serial_number' in self.details
        ):
            return {
                'cardMagEnc': self.details['mag_enc'],
                'serialNumber': self.details['mag_enc_serial_number'],
            }
        elif 'mag' in self.details:
            return {
                'cardMag': self.details['mag'],
            }

        raise ValueError('No valid payment details provided.')

    def process(self, **kwargs):
        """Makes a purchase request"""

        payment = self._determine_payment_details()

        purchase_data = {
            'accountId': self.api['account_id'],
            'apiToken': self.api['token'],
            'terminalId': self.api['terminal_id'],
            'transactionType': 'purchase',
            'test': 1 if kwargs.get('test', False) else 0,
            'amount': self.details['amount']
        }.update(payment)

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
