try:
    from oscar.apps.payment.exceptions import PaymentError
except ImportError:
    class PaymentError(Exception):
        pass

class HelcimError(PaymentError):
    pass