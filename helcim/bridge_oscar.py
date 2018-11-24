"""Bridging module between Django Oscar and gateway module."""
import logging

from oscar.apps.payment import exceptions as oscar_exceptions

from helcim import exceptions as helcim_exceptions, gateway
from helcim.models import HelcimToken

LOG = logging.getLogger(__name__)

# TODO: see if the token functions should be moved into gateway?

# TODO: see if the gateway module can collect all settings to more
# clearly set defaults

# TODO: when settings moved, rework any tests checking defaults
# (can test that a proper default is set rather than testing the function
# works with no setting specified)

def retrieve_token_details(token_id, customer):
    """Takes a HelcimToken ID and maps details to dictionary."""
    # Final validation to ensure token exists & belongs to proper user
    try:
        # Determine what identifier is used for tokens
        customer_reference = gateway.SETTINGS['token_vault_identifier']

        if customer_reference == 'helcim':
            token_instance = HelcimToken.objects.get(
                id=token_id, customer_code=customer
            )
        else:
            token_instance = HelcimToken.objects.get(
                id=token_id, django_user=customer
            )
    except HelcimToken.DoesNotExist:
        raise helcim_exceptions.ProcessingError(
            'Unable to retrieve token details for specified customer.'
        )

    # Validation passed - map model to the dictionary
    return {
        'token': token_instance.token,
        'token_f4l4': token_instance.token_f4l4,
        'customer_code': token_instance.customer_code,
    }

def remap_oscar_billing_address(address):
    """Remaps Oscar billing address dictionary to Helcim dictionary.

        Parameters:
            address (dict): A dictionary of the billing address details
                provided by Django Oscar.

        Returns:
            dict: Billing address details formatted for
                django-helcim.
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
            dict: Credit card details formatted for django-helcim.
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

def retrieve_saved_tokens(customer):
    """Returns list of tokens for specified customer.

        Parameters:
            customer: Either a a Django user instance or a Helcim
                customer code. The reference used is determined by the
                ``HELCIM_TOKEN_VAULT_IDENTIFIER`` setting.

        Returns:
            obj: A queryset of the retrieved tokens
    """
    # Determine what identifier is used for tokens
    customer_reference = gateway.SETTINGS['token_vault_identifier']

    if customer_reference == 'helcim':
        tokens = HelcimToken.objects.filter(customer_code=customer)
    else:
        tokens = HelcimToken.objects.filter(django_user=customer)

    return tokens

class BaseCardTransactionBridge():
    """Base class to bridge Oscar and Helcim transactions.

        Parameters:
            order_number (str): Order number for the transaction.
            amount (dec): The transaction total.
            card (obj): Instance of the Oscar bankcard class.
            billing_address (dict): The billing address information.
            save_token (bool): Whether the card token should be saved
                in the token vault or not.
            django_user (obj): The user to associate with the saved
                card token.
    """
    def __init__(
            self, order_number, amount, token_id=None, card=None,
            billing_address=None, save_token=False, django_user=None
    ):
        transaction_details = {
            'order_number': order_number,
            'amount': amount,
        }

        if token_id:
            transaction_details.update(retrieve_token_details(
                token_id, django_user
            ))

        if billing_address:
            transaction_details.update(remap_oscar_billing_address(
                billing_address
            ))

        if card:
            transaction_details.update(remap_oscar_credit_card(card))

        self.transaction_details = transaction_details
        self.save_token = save_token
        self.django_user = django_user

class PurchaseBridge(BaseCardTransactionBridge):
    """Class to bridge Oscar and Helcim purchase transactions."""
    def process(self):
        """Attempts to process Purchase with transaction details.

            Returns the values of ``gateway.Purchase.process``.

            Raises:
                GatewayError: An Oscar error raised when there was an
                    error with the payment API.
                PaymentError: An Oscar error raised when there was an
                    error processing the payment.
        """
        purchase_instance = gateway.Purchase(
            save_token=self.save_token,
            django_user=self.django_user,
            **self.transaction_details
        )

        try:
            return purchase_instance.process()
        except helcim_exceptions.ProcessingError as error:
            raise oscar_exceptions.GatewayError(str(error))
        except helcim_exceptions.PaymentError as error:
            raise oscar_exceptions.PaymentError(str(error))
        except helcim_exceptions.DjangoError:
            LOG.exception(
                'Purchase complete, but errors occured while saving '
                'transaction to database'
            )
        except helcim_exceptions.HelcimError as error:
            raise oscar_exceptions.GatewayError(str(error))

class PreauthorizeBridge(BaseCardTransactionBridge):
    """Class to bridge Oscar and Helcim preauthorization transactions."""
    def process(self):
        """Attempts to process Preauthorize with transaction details.

            Returns the values of ``gateway.Preauthorize.process``.

            Raises:
                GatewayError: An Oscar error raised when there was an
                    error with the payment API.
                PaymentError: An Oscar error raised when there was an
                    error processing the payment.
        """

        preauth_instance = gateway.Preauthorize(
            save_token=self.save_token,
            django_user=self.django_user,
            **self.transaction_details
        )

        try:
            return preauth_instance.process()
        except helcim_exceptions.ProcessingError as error:
            raise oscar_exceptions.GatewayError(str(error))
        except helcim_exceptions.PaymentError as error:
            raise oscar_exceptions.PaymentError(str(error))
        except helcim_exceptions.DjangoError:
            LOG.exception(
                'Preauthorization complete, but errors occured while saving '
                'transaction to database'
            )
        except helcim_exceptions.HelcimError as error:
            raise oscar_exceptions.GatewayError(str(error))

class RefundBridge(BaseCardTransactionBridge):
    """Class to bridge Oscar and Helcim refund transactions."""
    def process(self):
        """Attempts to process Refund with transaction details.

            Returns the values of ``gateway.Refund.process``.

            Raises:
                GatewayError: An Oscar error raised when there was an
                    error with the payment API.
                PaymentError: An Oscar error raised when there was an
                    error processing the payment.
        """

        refund_instance = gateway.Refund(
            save_token=self.save_token,
            django_user=self.django_user,
            **self.transaction_details
        )

        try:
            return refund_instance.process()
        except helcim_exceptions.ProcessingError as error:
            raise oscar_exceptions.GatewayError(str(error))
        except helcim_exceptions.PaymentError as error:
            raise oscar_exceptions.PaymentError(str(error))
        except helcim_exceptions.DjangoError:
            LOG.exception(
                'Refund complete, but errors occured while saving '
                'transaction to database'
            )
        except helcim_exceptions.HelcimError as error:
            raise oscar_exceptions.GatewayError(str(error))

class VerificationBridge(BaseCardTransactionBridge):
    """Class to bridge Oscar and Helcim Verification transactions."""
    def process(self):
        """Attempts to process Verification with transaction details.

            Returns the values of ``gateway.Verification.process``.

            Raises:
                GatewayError: An Oscar error raised when there was an
                    error with the payment API.
                PaymentError: An Oscar error raised when there was an
                    error processing the payment.
        """

        verification_instance = gateway.Verification(
            save_token=self.save_token,
            django_user=self.django_user,
            **self.transaction_details
        )

        try:
            return verification_instance.process()
        except helcim_exceptions.ProcessingError as error:
            raise oscar_exceptions.GatewayError(str(error))
        except helcim_exceptions.PaymentError as error:
            raise oscar_exceptions.PaymentError(str(error))
        except helcim_exceptions.DjangoError:
            LOG.exception(
                'Verification complete, but errors occured while saving '
                'transaction to database'
            )
        except helcim_exceptions.HelcimError as error:
            raise oscar_exceptions.GatewayError(str(error))

class CaptureBridge():
    """Class to bridge Oscar and Helcim Capture transactions.

        Parameters:
            transaction_id (int): the Helcim preauthorization
                 transaction ID to capture.
    """
    def __init__(self, transaction_id):
        transaction_details = {
            'transaction_id': transaction_id,
        }

        self.transaction_details = transaction_details

    def process(self):
        """Attempts to process Capture with transaction details.

            Returns the values of ``gateway.Capture.process``.

            Raises:
                GatewayError: An Oscar error raised when there was an
                    error with the payment API.
                PaymentError: An Oscar error raised when there was an
                    error processing the payment.
        """

        capture_instance = gateway.Capture(
            **self.transaction_details
        )

        try:
            return capture_instance.process()
        except helcim_exceptions.ProcessingError as error:
            raise oscar_exceptions.GatewayError(str(error))
        except helcim_exceptions.PaymentError as error:
            raise oscar_exceptions.PaymentError(str(error))
        except helcim_exceptions.DjangoError:
            LOG.exception(
                'Capture complete, but errors occured while saving '
                'transaction to database'
            )
            return None
        except helcim_exceptions.HelcimError as error:
            raise oscar_exceptions.GatewayError(str(error))
