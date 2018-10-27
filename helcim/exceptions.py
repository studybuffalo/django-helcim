"""Custom exceptions for package, Helcim API, and django-oscar"""

class HelcimError(Exception):
    """Base exception for all package exceptions."""
    pass

class ProcessingError(HelcimError):
    """Exceptions to handle system and API connection errors."""
    pass

class PaymentError(HelcimError):
    """Exceptions to handle payment and refund errors."""
    pass
