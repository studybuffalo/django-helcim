"""Process and validates data to and from the Helcim API."""

from datetime import datetime
from decimal import Decimal
import logging

LOG = logging.getLogger(__name__)

class Field(object):
    """A single API field.

    Parameters:
        api_name (str): The Helcim API field name for the field.
        field_type (str): The field type: ``s`` (string), ``c``
            (decimal), ``i`` (integer), ``b`` (boolean), ``d`` (date),
            or ``t`` (time).
        min (int, optional): The minimum field length.
        max (int, optional): The maximum field length.
    """

    def __init__(
            self, api_name, field_type='s',
            min_length=None, max_length=None
    ):
        # Ensure a valid field type is provided
        if field_type not in ['s', 'c', 'i', 'b', 'd', 't']:
            raise ValueError(
                'Invalid field type provided for {}: {}'.format(
                    api_name, field_type
                )
            )

        self.field_name = api_name
        self.field_type = field_type
        self.min = min_length
        self.max = max_length

TO_API_FIELDS = {
    'amount': Field('amount', 'c'),
    'amount_shipping': Field('amountShipping', 'c'),
    'amount_tax': Field('amountTax', 'c'),
    'billing_business_name': Field('billing_businessName', 's'),
    'billing_city': Field('billing_city', 's'),
    'billing_contact_name': Field('billing_contactName', 's'),
    'billing_country': Field('billing_country', 's'),
    'billing_email': Field('billing_email', 's'),
    'billing_fax': Field('billing_fax', 's'),
    'billing_phone': Field('billing_phone', 's'),
    'billing_postal_code': Field('billing_postalCode', 's'),
    'billing_province': Field('billing_province', 's'),
    'billing_street_1': Field('billing_street1', 's'),
    'billing_street_2': Field('billing_street2', 's'),
    'cc_address': Field('cardHolderAddress', 's'),
    'cc_cvv': Field('cardCVV', 's', 3, 4),
    'cc_expiry': Field('cardExpiry', 's', 4, 4),
    'cc_name': Field('cardHolderName', 's'),
    'cc_number': Field('cardNumber', 's', 16, 16),
    'cc_postal_code': Field('cardHolderPostalCode', 's'),
    'comments': Field('comments', 's'),
    'customer_code': Field('customerCode', 's'),
    'ecommerce': Field('ecommerce', 'b'),
    'ip_address': Field('ipAddress', 's', 7, 45),
    'mag': Field('cardMag', 's'),
    'mag_enc': Field('cardMagEnc', 's'),
    'mag_enc_serial_number': Field('serialNumber', 's'),
    'order_number': Field('orderNumber', 's'),
    'product_id': Field('productId', 'i', 1),
    'shipping_business_name': Field('shipping_businessName', 's'),
    'shipping_city': Field('shipping_city', 's'),
    'shipping_contact_name': Field('shipping_contactName', 's'),
    'shipping_country': Field('shipping_country', 's'),
    'shipping_email': Field('shipping_email', 's'),
    'shipping_fax': Field('shipping_fax', 's'),
    'shipping_method': Field('shipping_method', 's'),
    'shipping_phone': Field('shipping_phone', 's'),
    'shipping_postal_code': Field('shipping_postalCode', 's'),
    'shipping_province': Field('shipping_province', 's'),
    'shipping_street_1': Field('shipping_street1', 's'),
    'shipping_street_2': Field('shipping_street2', 's'),
    'tax_details': Field('taxDetails', 's'),
    'test': Field('test', 'b'),
    'token': Field('cardToken', 's', 23, 23),
    'token_f4l4': Field('cardF4L4', 's', 8, 8),
    'token_f4l4_skip': Field('cardF4L4Skip', 'b'),
    'transaction_id': Field('transactionId', 'i', 0),
}

FROM_API_FIELDS = {
    'amount': Field('amount', 'c'),
    'availability': Field('availability', 'b'),
    'approvalCode': Field('approval_code', 's'),
    'avsResponse': Field('avs_response', 's'),
    'cardHolderName': Field('cc_name', 's'),
    'cardNumber': Field('cc_number', 's'),
    'cardToken': Field('token', 's'),
    'cardType': Field('cc_type', 's'),
    'currency': Field('currency', 's'),
    'customerCode': Field('customer_code', 's'),
    'cvvResponse': Field('cvv_response', 's'),
    'date': Field('transaction_date', 'd'),
    'expiryDate': Field('cc_expiry', 's'),
    'orderNumber': Field('order_number', 's'),
    'time': Field('transaction_time', 't'),
    'transactionId': Field('transaction_id', 'i'),
    'type': Field('transaction_type', 's'),
}

def validate_request_fields(details):
    """Validates and coerces request field data prior to submission.

    Uses the TO_API_FIELDS dictionary to determine type and required
    validation to apply.

    Parameters:
        details (dict): The values to validated and coerce.

    Returns:
        dict: The cleaned data (with the same keys as ``details``).

    Raises:
        ValueError: Raised if data fails validation.
    """
    cleaned = {}

    for field_name, field_value in details.items():
        validation = TO_API_FIELDS[field_name]

        # Coerce value and any validation
        # String Types
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

        # Integer types
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

        # Decimal types
        elif validation.field_type == 'c':
            cleaned_value = Decimal(str(field_value))

            if validation.min and cleaned_value < validation.min:
                raise ValueError(
                    '{} field value too small.'.format(field_name)
                )

            if validation.max and cleaned_value > validation.max:
                raise ValueError(
                    '{} field value too large.'.format(field_name)
                )

        # Boolean types
        elif validation.field_type == 'b':
            cleaned_value = 1 if bool(field_value) else 0

        # Add the field to the cleaned data
        cleaned[field_name] = cleaned_value

    return cleaned

def process_request_fields(api, cleaned, additional=None):
    """Converts all data to proper Helcim API request fields.

    Parameters:
        api (dict): The API setting fields.
        cleaned(dict): The cleaned POST data.
        additional: Any additional POST data to directly add (skips
            any conversion steps).

    Returns:
        dict: The data ready for a POST request.
    """
    request_data = {}

    # API Data
    request_data['accountId'] = str(api['account_id'])
    request_data['apiToken'] = str(api['token'])
    request_data['terminalId'] = str(api['terminal_id'])

    # Cleaned Data
    for field_name, field_value in cleaned.items():
        request_data[TO_API_FIELDS[field_name].field_name] = str(field_value)

    # Combine with the additional data
    if additional:
        request_data.update(additional)

    return request_data

def create_raw_request(data):
    """Converts the raw request into a POST string.

    Parameters:
        data (dict): The POST request data dictionary.

    Returns:
        str: The POST request data as a formatted string.
    """
    if data:
        raw_strings = []

        for key, item in data.items():
            raw_strings.append('{}={}'.format(key, item))

        return '&'.join(raw_strings)

    return data

def process_api_response(response, raw_request=None, raw_response=None):
    """Updates API field names/types, and adds additional data.

    Parameters:
        response (str): The API response (as an ``OrderedDict``).
        raw_request (str): Raw request (as string) submitted to API.
        raw_response (str): Raw response (as string) returned by API.

    Returns:
        dict: The validated and convereted API response.
    """
    # Add the standard API response details
    processed = {
        'transaction_success': (
            True if int(response['response']) == 1 else False
        ),
        'response_message': str(response['responseMessage']),
        'notice': str(response['notice']),
    }

    # Add and coerece any fields returned in the transaction field
    if 'transaction' in response:
        for field_name, field_value in response['transaction'].items():

            try:
                api_field = FROM_API_FIELDS[field_name]
                new_name = api_field.field_name

                # String Field
                if api_field.field_type == 's':
                    processed[new_name] = str(field_value)

                # Decimal Field
                elif api_field.field_type == 'c':
                    processed[new_name] = Decimal(field_value)

                # Integer Field
                elif api_field.field_type == 'i':
                    processed[new_name] = int(field_value)

                # Boolean Field
                elif api_field.field_type == 'b':
                    processed[new_name] = True if field_value == '1' else False

                # Date Field
                elif api_field.field_type == 'd':
                    processed[new_name] = datetime.strptime(
                        field_value, '%Y-%m-%d'
                    ).date()

                # Time Field
                elif api_field.field_type == 't':
                    processed[new_name] = datetime.strptime(
                        field_value, '%H:%M:%S'
                    ).time()
            except KeyError:
                LOG.warning(
                    'Response field not in FROM_API_FIELDS: %s', field_name
                )
                processed[field_name] = field_value

        # If possible, create the F4L4 field
        cc_number = processed.get('cc_number')

        if cc_number:
            processed['token_f4l4'] = '{}{}'.format(
                cc_number[:4], cc_number[-4:]
            )
        else:
            processed['token_f4l4'] = None

    # Add additional audit information
    processed['raw_request'] = create_raw_request(raw_request)
    processed['raw_response'] = raw_response

    return processed
