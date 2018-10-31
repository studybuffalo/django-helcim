"""Custom exceptions for django-helcim."""

class HelcimError(Exception):
    """Base exception for all package exceptions."""
    pass

class ProcessingError(HelcimError):
    """Exception to handle system and API connection errors."""
    pass

class PaymentError(HelcimError):
    """Exception to handle payments, pre-auths, and captures."""
    pass

class RefundError(HelcimError):
    """Exception to handle refund errors."""
    pass

class VerificationError(HelcimError):
    """Exception to handle errors during credit care verification."""
    pass

class DjangoError(HelcimError):
    """Exception for issues relating to Django interface."""
    pass
