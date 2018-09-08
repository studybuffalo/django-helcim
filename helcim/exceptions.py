"""Custom exceptions for package, Helcim API, and django-oscar"""

try:
    from oscar.apps.payment.exceptions import PaymentError
except ImportError:
    class PaymentError(Exception):
        """Error to allow proper error handling with django-oscar"""
        pass

class HelcimError(PaymentError):
    """Extended PaymentError to improve agnostic interfacing"""
    pass
