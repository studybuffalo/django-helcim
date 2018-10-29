"""Views for the Helcim checkout."""
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from oscar.apps.checkout import views
from oscar.apps.payment import forms, models

from helcim import bridge_oscar

class PaymentDetailsView(views.PaymentDetailsView):
    """Collects and processes payment details."""

    def get_context_data(self, **kwargs):
        """Add additional data for payment processing."""
        context = super(PaymentDetailsView, self).get_context_data(**kwargs)

        # Add the credit card data
        context['bankcard_form'] = kwargs.get(
            'bankcard_form', forms.BankcardForm()
        )

        # Add the billing address data
        context['billing_address_form'] = kwargs.get(
            'billing_address_form', forms.BillingAddressForm()
        )

        return context

    def post(self, request, *args, **kwargs):
        """Makes the POST request that triggers payment processing."""

        # If action is place order, start payment processing
        if request.POST.get('action', '') == 'place_order':
            return self.do_place_order(request)

        # Validate the credit card and billing address forms
        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = forms.BillingAddressForm(request.POST)

        if not all([
                bankcard_form.is_valid(), billing_address_form.is_valid()
        ]):
            # Validation failed, render page again with errors
            self.preview = False

            context = self.get_context_data(
                bankcard_form=bankcard_form,
                billing_address_form=billing_address_form,
            )

            return self.render_to_response(context)

        # Render the preview with the credit card and billing
        # address details (hidden)
        return self.render_preview(
            request,
            bankcard_form=bankcard_form,
            billing_address_form=billing_address_form,
        )

    def do_place_order(self, request):
        """Helper method to check that hiddens forms were not modified."""
        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = forms.BillingAddressForm(request.POST)

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
        return self.submit(**submission)

    def handle_payment(self, order_number, total, **kwargs):
        """Submit payment details to the Helcim Commerce API."""
        # Make a purchase request to the Helcim Commerce API
        purchase = bridge_oscar.PurchaseBridge(
            order_number=order_number,
            amount=total.incl_tax,
            card=kwargs['bankcard'],
            billing_address=kwargs['billing_address']
        )
        purchase.process()

        # Record payment source and event
        source_type, _ = models.SourceType.objects.get_or_create(
            name='Helcim')

        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            currency=total.currency
        )
        self.add_payment_source(source)
        self.add_payment_event('Authorised', total.incl_tax)
