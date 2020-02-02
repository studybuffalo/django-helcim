"""Custom Checkout Application."""
import oscar.apps.checkout.apps as apps


class CheckoutConfig(apps.CheckoutConfig):
    """App configuration for custom checkout."""
    name = 'applications.checkout'
