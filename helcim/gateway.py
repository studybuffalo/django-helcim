"""Interface functions with the Helcim Commerce API.

These functions provide a interface with the Helcim Commerce API.
These functions are agnostic and should work in any applications (i.e.
not just django-oscar).
"""

import requests
import xmltodict


def post(url, post_data=None):
    """Makes POST to Helcim API and provides response as dictionary.

    Args:
        url (str): URL to the Helcim API.
        post_data (dict): The parameters to pass with the POST request.

    Returns:
        dict: The API response.

    Raises:
        ValueError: TBD.

    """

    # Setup the POST header
    post_headers = {'content-type': 'text/plain; charset=utf-8'}

    # Make the POST request
    response = requests.post(url, post_data, headers=post_headers)

    # Error handling

    # Return the response
    return xmltodict.parse(response)

# TODO: Add validation of payment details

def determine_payment_details(details):
    """Returns most appropriate payment details for Helcim API request.

    Cycles through the provided details to determine the most
    appropriate payment method. If multiple methods provided, only the
    first match is returned (token > customer code > CC number >
    encrypted magnetic strip > magnetic strip).

    Args:
        details (dict): A dictionary of payment details (typically
            provided by **kwargs).
    Returns:
        dict: Dictionary of the appropriate payment details.
    Raises:
        ValueError: No valid payment details provided.
    """

    if 'token' in details and 'customer_code' in details:
        # F4L4 required or it must be explicitly skipped
        f4l4_skip = details.get('token_f4l4_skip', False)

        if f4l4_skip:
            return {
                'cardToken': details['token'],
                'customerCode': details['customer_code'],
                'cardF4L4Skip': 1,
            }

        if 'token_f4l4' in details:
            return {
                'cardToken': details['token'],
                'customerCode': details['customer_code'],
                'cardF4L4': details['token_f4l4'],
            }

    elif 'customer_code' in details:
        return {
            'customerCode': details['customer_code']
        }

    elif 'cc_number' in details and 'cc_expiry' in details:
        cc_details = {
            'cardNumber': details['cc_number'],
            'cardexpiry': details['cc_expiry'],
        }

        # Add any additional CC details (as provided)
        if 'cc_name' in details:
            cc_details.update(
                {'cardHolderName': details['cc_name']}
            )

        if 'cc_cvv' in details:
            cc_details.update(
                {'cardCVV': details['cc_cvv']}
            )

        if 'cc_address' in details:
            cc_details.update(
                {'cardHolderAddress': details['cc_address']}
            )

        if 'cc_postal_code' in details:
            cc_details.update(
                {'cardHolderPostalCode': details['cc_postal_code']}
            )

        return cc_details

    elif 'mag_enc' in details and 'mag_enc_serial_number' in details:
        return {
            'cardMagEnc': details['mag_enc'],
            'serialNumber': details['mag_enc_serial_number'],
        }
    elif 'mag' in details:
        return {
            'cardMag': details['mag'],
        }

    raise ValueError('No valid payment details provided.')

def purchase(api_details, amount, payment_details, **kwargs):
    """Makes a purchase request
    Args:
        api_credentials (dict): Details to connect to Helcim Commerce
            API:

            url (str): API URL.
            account_id (str): Helcim account ID.
            token (str): Helcim API token.
            terminal (str): Helcim terminal ID.

        amount (dec): The amount being purchased.
        payment_details (dict): Details on the payment method:

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

        **kwargs: Payment, billing, shipping, and other details.

    Keyword Args:
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

    payment = determine_payment_details(payment_details)

    purchase_data = {
        'accountId': api_details['account_id'],
        'apiToken': api_details['token'],
        'terminalId': api_details['terminal_id'],
        'transactionType': 'purchase',
        'test': 1 if kwargs.get('test', False) else 0,
        'amount': amount
    }.update(payment)

    return post(api_details['url'], purchase_data)

def refund():
    """Makes a refund request
    """

    pass

def verify():
    """Makes a verification request
    """

    pass

def preauthorize():
    """Makes a pre-authorization request
    """

    pass

def capture():
    """Makes a capture request (to complete a preauthorization)
    """

    pass
