"""Provides data and validation information for Helcim API fields."""

class Field(object):
    """A single API field.

    Attributes:
        api_name (str): The Helcim API field name for the field.
        field_type (str): The field type: ``s`` (string), ``d`` (decimal),
            ``i`` (integer), or ``b`` (boolean).
        min (int, optional): The minimum field length.
        max (int, optional): The maximum field length.
    """

    def __init__(
            self, api_name, field_type='s',
            min_length=None, max_length=None
    ):
        self.api_name = api_name
        self.field_type = field_type
        self.min = min_length
        self.max = max_length


FIELD_LIST = {
    'amount': Field('amount', 'd'),
    'amount_shipping': Field('amountShipping', 'd'),
    'amount_tax': Field('amountTax', 'd'),
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
    'mag': Field('cardMag', 's'),
    'mag_enc': Field('cardMagEnc', 's'),
    'mag_enc_serial_number': Field('serialNumber', 's'),
    'order_number': Field('orderNumber', 's'),
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
    'token': Field('cardToken', 's', 23, 23),
    'token_f4l4': Field('cardF4L4', 's', 8, 8),
    'token_f4l4_skip': Field('cardF4L4Skip', 'b'),
}
