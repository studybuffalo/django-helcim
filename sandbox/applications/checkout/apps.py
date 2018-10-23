"""Apps configuration for the Helcim checkout."""
from oscar.apps.checkout import app

from applications.checkout import views


class CheckoutApplication(app.CheckoutApplication):
    """Extended Django-Oscar checkout application."""
    payment_details_view = views.PaymentDetailsView


application = CheckoutApplication()
