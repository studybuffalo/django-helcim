"""
Bridging module between Oscar and gateway module (which is Oscar agnostic).
"""
from __future__ import unicode_literals

# from oscar.apps.payment import exceptions

from . import gateway # models

def sale(order_number, amount, card, billing_address=None):
    """Make a sale request.

    Attributes
        order_number (str): Order number for the transaction.
        amount (dec): The transaction total.
        card (obj): Instance of the Oscar bankcard class.
        billing_address (dict): The billing address information.

    Raises:
        OscarError: Various types of Oscar error codes.
    """
    # TODO: Clarify attribute types, types of errors that can be raised.
    purchase = gateway.Purchase(
        {
            'url': '',
            'account_id': '',
            'token': '',
            'terminal': '',
        },
        order_number=order_number,
        amount=amount,
        cc=card,
        billing_address=billing_address,
    )
    return purchase.process()

# def authorize(order_number, amount, card, billing_address=None):
#     """Make an authorization request.

#     Authorization requests confirms and holds the money from a
#     customer's account, but does not settle the transaction. The
#     transaction is settled by calling the delayed_capture method. This
#     is a common workflow for products that require shipping.

#     Attributes
#         order_number (str): Order number for the transaction.
#         amount (dec): The transaction total.
#         card (obj): Instance of the Oscar bankcard class.
#         billing_address (dict): The billing address information.

#     Raises:
#         OscarError: Various types of Oscar error codes.
#     """

#     return _submit_payment_details(
#         gateway.preauthorize, order_number, amount, card, billing_address
#     )



# def delayed_capture(order_number, pnref=None, amt=None):
#     """
#     Capture funds that have been previously authorized.
#     Notes:
#     * It's possible to capture a lower amount than the original auth
#       transaction - however...
#     * ...only one delayed capture is allowed for a given PNREF...
#     * ...If multiple captures are required, a 'reference transaction'
#          needs to be
#       used.
#     * It's safe to retry captures if the first one fails or errors
#     :order_number: Order number
#     :pnref: The PNREF of the authorization transaction to use.  If not
#             specified, the order number is used to retrieve the appropriate
#             transaction.
#     :amt: A custom amount to capture.
#     """
#     if pnref is None:
#         # No PNREF specified, look-up the auth transaction for this order
#         # number
#         # to get the PNREF from there.
#         try:
#             auth_txn = models.PayflowTransaction.objects.get(
#                 comment1=order_number, trxtype=codes.AUTHORIZATION)
#         except models.PayflowTransaction.DoesNotExist:
#             raise exceptions.UnableToTakePayment(
#                 "No authorization transaction found with PNREF=%s" % pnref)
#         pnref = auth_txn

#     txn = gateway.delayed_capture(order_number, pnref, amt)
#     if not txn.is_approved:
#         raise exceptions.UnableToTakePayment(txn.respmsg)
#     return txn


# def referenced_sale(order_number, pnref, amt):
#     """
#     Capture funds using the bank/address details of a previous transaction
#     This is equivalent to a *sale* transaction but without the user having to
#     enter their payment details.
#     There are two main uses for this:
#     1. This allows customers to checkout without having to re-enter their
#        payment details.
#     2. It allows an initial authorisation to be settled in multiple parts.
#        The first settle should use delayed_capture but any subsequent ones
#        should use this method.
#     :order_number: Order number.
#     :pnref: PNREF of a previous transaction to use.
#     :amt: The amount to settle for.
#     """
#     txn = gateway.reference_transaction(
#         order_number, pnref, amt)
#     if not txn.is_approved:
#         raise exceptions.UnableToTakePayment(txn.respmsg)
#     return txn


# def void(order_number, pnref):
#     """
#     Void an authorisation transaction to prevent it from being settled
#     :order_number: Order number
#     :pnref: The PNREF of the transaction to void.
#     """
#     txn = gateway.void(order_number, pnref)
#     if not txn.is_approved:
#         raise exceptions.PaymentError(txn.respmsg)
#     return txn


# def credit(order_number, pnref=None, amt=None):
#     """
#     Return funds that have been previously settled.
#     :order_number: Order number
#     :pnref: The PNREF of the authorization transaction to use.  If not
#             specified, the order number is used to retrieve the appropriate
#             transaction.
#     :amt: A custom amount to capture.  If not specified, the entire
#           transaction is refuneded.
#     """
#     if pnref is None:
#         # No PNREF specified, look-up the auth/sale transaction for this
#         # order number to get the PNREF from there.
#         try:
#             auth_txn = models.PayflowTransaction.objects.get(
#                 comment1=order_number, trxtype__in=(codes.AUTHORIZATION,
#                                                     codes.SALE))
#         except models.PayflowTransaction.DoesNotExist:
#             raise exceptions.UnableToTakePayment(
#                 "No authorization transaction found with PNREF=%s" % pnref)
#         pnref = auth_txn

#     txn = gateway.credit(order_number, pnref, amt)
#     if not txn.is_approved:
#         raise exceptions.PaymentError(txn.respmsg)
#     return txn
