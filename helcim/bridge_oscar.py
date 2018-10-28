"""Bridging module between Django Oscar and gateway module."""
from __future__ import unicode_literals

from oscar.apps.payment import exceptions as oscar_exceptions

from helcim import exceptions as helcim_exceptions, gateway

def remap_oscar_billing_address(address):
    """Remaps Oscar billing address dictionary to Helcim dictionary.

        Parameters:
            address (dict): A dictionary of the billing address details
                provided by Django Oscar.

        Returns:
            dict: Billing address details formatted for
                django-oscar-helcim.
    """
    if address.get('first_name') and address.get('last_name'):
        contact_name = '{} {}'.format(
            address.get('first_name'), address.get('last_name')
        )
    elif address.get('first_name'):
        contact_name = address.get('first_name')
    elif address.get('last_name'):
        contact_name = address.get('last_name')
    else:
        contact_name = None

    return {
        'billing_contact_name': contact_name,
        'billing_street_1': address.get('line1'),
        'billing_street_2': address.get('line2'),
        'billing_city': address.get('line4'),
        'billing_province': address.get('state'),
        'billing_postal_code': address.get('postcode'),
        'billing_country': address.get('country'),
        'billing_phone': address.get('phone_number'),
    }

def remap_oscar_credit_card(card):
    """Remaps Oscar credit card object as Helcim dictionary.

        Parameters:
            card (obj): A credit card object provided by Django Oscar.

        Returns:
            dict: Credit card details formatted for django-oscar-helcim.
    """
    if card.expiry_date:
        cc_expiry = card.expiry_date.strftime('%m%y')
    else:
        cc_expiry = None

    return {
        'cc_name': card.name,
        'cc_number': card.number,
        'cc_expiry': cc_expiry,
        'cc_cvv': card.ccv,
    }

def purchase(order_number, amount, card, billing_address=None):
    """Make a purchase request.

    Parameters:
        order_number (str): Order number for the transaction.
        amount (dec): The transaction total.
        card (obj): Instance of the Oscar bankcard class.
        billing_address (dict): The billing address information.

    Raises:
        GatewayError: An Oscar error raised when there was an error
            with the payment API.
        PaymentError: An Oscar error raised when there was an error
            processing the payment.
    """

    purchase_details = {
        'order_number': order_number,
        'amount': amount,
    }

    if billing_address:
        purchase_details.update(remap_oscar_billing_address(billing_address))

    purchase_details.update(remap_oscar_credit_card(card))

    purchase_instance = gateway.Purchase(**purchase_details)

    try:
        return purchase_instance.process()
    except helcim_exceptions.ProcessingError as error:
        raise oscar_exceptions.GatewayError(str(error))
    except helcim_exceptions.PaymentError as error:
        raise oscar_exceptions.PaymentError(str(error))
    except helcim_exceptions.HelcimError as error:
        raise oscar_exceptions.GatewayError(str(error))
