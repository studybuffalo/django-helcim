"""Views for the Helcim checkout."""
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from oscar.apps.checkout import views
from oscar.apps.payment import (
    models as oscar_payment_models, forms as oscar_payment_forms
)

from helcim import bridge_oscar

from applications.checkout import forms as custom_forms

class PaymentDetailsView(views.PaymentDetailsView):
    """Collects and processes payment details."""
    def get_context_data(self, **kwargs):
        """Add additional data for payment processing."""
        context = super(PaymentDetailsView, self).get_context_data(**kwargs)

        # Add the credit card data
        context['bankcard_form'] = kwargs.get(
            'bankcard_form', oscar_payment_forms.BankcardForm()
        )

        # Add the billing address data
        context['billing_address_form'] = kwargs.get(
            'billing_address_form', custom_forms.BillingAddressForm()
        )

        # Add details regarding saved credit card tokens
        context['token_vault'] = getattr(
            settings, 'HELCIM_ENABLE_TOKEN_VAULT', False
        )
        context['saved_tokens'] = bridge_oscar.retrieve_saved_tokens(
            self.request.user
        )

        return context

    def post(self, request, *args, **kwargs):
        """Makes the POST request that moves between views.

        If POST has an 'action' of 'place_order' the payment processing
        can begin (call 'do_place_order').

        If POST has no 'action' this would be an attempt to move to the
        preview screen. A set of forms needs to be valid to proceed
        (either the 'saved_card_token_form' or both the 'bankcard_form'
        and 'billing_address_form'). If not, return the forms with the
        error messages.
        """
        # Need to work out handling of bank card vs. token here
        # May find help here:
        # https://github.com/sdonk/oscar-sagepay/blob/master/code/sagepay/views.py

        # Check if payment can be processed
        if request.POST.get('action', None) == 'place_order':
            return self.do_place_order(request)

        # TODO: Handle both new card and old card validation here

        # Check if forms are valid and preview screen can be displayed
        bankcard_form = oscar_payment_forms.BankcardForm(request.POST)
        billing_address_form = custom_forms.BillingAddressForm(request.POST)

        if not (bankcard_form.is_valid() and billing_address_form.is_valid()):
            self.preview = False

            # Reload the form content for the user
            context = self.get_context_data(
                bankcard_form=bankcard_form,
                billing_address_form=billing_address_form,
            )

            return self.render_to_response(context)

        # Render the preview page
        return self.render_preview(
            request,
            bankcard_form=bankcard_form,
            billing_address_form=billing_address_form,
        )

    def do_place_order(self, request):
        """Helper method to check that hiddens forms were not modified."""
        # Need to work out handling of bank card vs. token here
        # May find help here:
        # https://github.com/sdonk/oscar-sagepay/blob/master/code/sagepay/views.py

        # saved_card_token_form here (probably throw this into the bridge module)
        bankcard_form = oscar_payment_forms.BankcardForm(request.POST)
        billing_address_form = custom_forms.BillingAddressForm(request.POST)

        # Require either set of forms to be valid; token supercedes
        # entered card data
        if not all([
                bankcard_form.is_valid(),
                billing_address_form.is_valid()
        ]):
            # Forms now have errors, return to payment page
            messages.error(request, "Invalid submission")
            return HttpResponseRedirect(reverse('checkout:payment-details'))

        # Submit the order along with the required payment details
        # (these will be passed along for payment processing)
        submission = self.build_submission()
        submission['payment_kwargs']['bankcard'] = bankcard_form.bankcard
        submission['payment_kwargs']['billing_address'] = (
            billing_address_form.cleaned_data
        )
        # Can we add a token field to payment_kwargs to pass through?
        return self.submit(**submission)

    def handle_payment(self, order_number, total, **kwargs):
        """Submit payment details to the Helcim Commerce API."""
        # Need to work out a "universal" handling of CC vs. token
        # Make a purchase request to the Helcim Commerce API
        purchase = bridge_oscar.PurchaseBridge(
            order_number=order_number,
            amount=total.incl_tax,
            card=kwargs['bankcard'],
            billing_address=kwargs['billing_address'],
            save_token=kwargs['billing_address'].get('save_card', False),
            django_user=self.request.user,
        )
        purchase.process()

        # Record payment source and event
        source_type, _ = oscar_payment_models.SourceType.objects.get_or_create(
            name='Helcim'
        )

        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            currency=total.currency,
        )
        self.add_payment_source(source)
        self.add_payment_event('Authorised', total.incl_tax)
