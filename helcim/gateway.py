import requests
import xmltodict


def post(url, post_data={}):
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

def determine_payment_details(details):
    """Identifies which payment details have been provided.

    Cycles through the provided details to determine the most
    appropriate payment method. If multiple methods provided, only the
    first match is returned (token > customer code > CC number >
    encrypted magnetic strip > magnetic strip).

    Args:
        details (dict): A dictionary of payment details (typically
            provided by **kwargs).
    Returns:
        str: the payment type detected
    Raises:
        SomeError: No valid payment details provided.
    """

    if 'card_token' in details and 'customer_code' in details:
        return 'token'
    elif 'customer_code' in details:
        return 'customer'
    elif 'cc_number' in details and 'cc_expiry' in details:
        return 'cc'
    elif 'cc_mag_encrypted' in details and 'serial_number' in details:
        return 'mage'
    elif 'cc_mag' in details:
        return 'mag'

    raise ValueError('No valid payment type identified.')

def purchase(amount, **kwargs):
    """Makes a purchase request
    Args:
        amount (dec): The amount being purchased.
        **kwargs: Payment, billing, shipping, and other details.

    Keyword Args:
        cc_cardholder_name (str, optional): Name of the credit
            cardholder.
        cc_number (int, optional): 16 digit credit card number.
        cc_expiry (int, optional): 4 digit (MMYY) credit card expiry.
        cc_cvv (int, optional): 3 digit credit card CVV.
        cc_address (str, optional): Address of the credit cardholder.
        cc_postal_code (str, optional): Postal code/zip code of the
            credit cardholder.
        customer_code (str, optional): Helcim customer code.
        card_token (str, optional): 23 digit Helcim card token.
        cc_f4_l4 (int, optional): 8 digit "first four digits and last
            four digits" of the credit card number
        cc_f4_l4_skip (bool, optional): Whether to skip the F4L4
            verification.
        cc_mag (string, optional): Non-encrypted credit card magnetic
            strip data.
        serial_number (string, optional): Terminal serial number.
        cc_mag_encrypted (str, optional): Encrypted credit card
            magnestic strip data.
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
    # TODO: Will need to work out handling new card vs. token vs. customer code


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
