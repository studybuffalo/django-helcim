"""Application config to add helcim payment app."""
from oscar.app import Shop

from applications.checkout.apps import application as checkout_app


class HelcimShop(Shop):
    """Extending Django-Oscar shop to include Helcim payments"""
    checkout_app = checkout_app

application = HelcimShop() # pylint: disable=invalid-name
