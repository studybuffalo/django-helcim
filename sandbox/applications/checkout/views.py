"""Views for the Helcim checkout."""
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from oscar.apps.checkout import views
from oscar.apps.payment import (
    models as oscar_payment_models, forms as oscar_payment_forms
)

from helcim import bridge_oscar
from helcim.models import HelcimToken

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
        context['token_vault'] = bridge_oscar.SETTINGS['enable_token_vault']
        context['saved_tokens'] = bridge_oscar.retrieve_saved_tokens(
            self.request.user
        )

        return context

    def post(self, request, *args, **kwargs):
        """Makes the POST request that moves between views.

            If POST has an 'action' of 'place_order' the payment
            processing can begin (call 'do_place_order').

            If POST has no 'action' this would be an attempt to move to
            thepreview screen. The payment details (token or credit
            card) must be valid to proceed. If not, return to the
            payment page to display any error messages and allow
            resubmission.
        """
        # Check if payment can be processed
        if request.POST.get('action', None) == 'place_order':
            return self.do_place_order(request)

        # Not a payment POST - will need to validate payment details
        token_id = request.POST.get('token-id', None)

        # Token present - validate and return preview
        if token_id:
            token_instance = HelcimToken.objects.filter(id=token_id).first()

            # If no instance, this is invalid
            if not token_instance:
                self.preview = False

                # Reload the payment page with the errors
                messages.warning(
                    request,
                    (
                        'There was an issue retrieving the saved credit card '
                        'information. You may retry the card again or '
                        're-enter the details below.'
                    )
                )
                return self.render_to_response(self.get_context_data)

            # Instance found - can move to preview
            return self.render_preview(
                request,
                token_id=token_id,
            )

        # No token present - validate credit card information
        bankcard_form = oscar_payment_forms.BankcardForm(request.POST)
        address_form = custom_forms.BillingAddressForm(request.POST)

        # Check that bank card data is valid
        if not (bankcard_form.is_valid() and address_form.is_valid()):
            self.preview = False

            # Reload the payment page with the errors
            context = self.get_context_data(
                bankcard_form=bankcard_form,
                billing_address_form=address_form,
            )

            return self.render_to_response(context)

        # Render the preview page
        return self.render_preview(
            request,
            bankcard_form=bankcard_form,
            billing_address_form=address_form,
        )

    def do_place_order(self, request):
        """Re-validates payments details and sends for processing.

            Payment details are hidden on the preview page. They are
            re-validated to ensure no tampering and then added to the
            order details for actual payment processing.
        """
        token_id = request.POST.get('token-id', None)

        # Token takes precedence over any other payment methods
        if token_id:
            token_instance = HelcimToken.objects.filter(id=token_id).first()

            if not token_instance:
                # Issue with token now, return to payment page
                messages.error(request, 'Invalid submission')
                return HttpResponseRedirect(
                    reverse('checkout:payment-details')
                )

            # Add token_id to order details
            submission = self.build_submission()
            submission['payment_kwargs']['token_id'] = token_id
        else:
            bankcard_form = oscar_payment_forms.BankcardForm(request.POST)
            address_form = custom_forms.BillingAddressForm(request.POST)

            # Confirm no errors since payment page
            if not (bankcard_form.is_valid() and address_form.is_valid()):
                # Forms now have errors, return to payment page
                messages.error(request, 'Invalid submission')
                return HttpResponseRedirect(
                    reverse('checkout:payment-details')
                )

            # Add bank card information to order details
            submission = self.build_submission()
            submission['payment_kwargs']['bankcard'] = bankcard_form.bankcard
            submission['payment_kwargs']['billing_address'] = (
                address_form.cleaned_data
            )

        return self.submit(**submission)

    def handle_payment(self, total, **kwargs):
        """Submit payment details to the Helcim Commerce API."""
        # Extract all payment details
        token_id = kwargs.get('token_id', None)
        card_details = kwargs.get('bankcard', None)
        billing_address = kwargs.get('billing_address', None)

        if billing_address:
            save_token = billing_address.get('save_card', False)
        else:
            save_token = False

        # Make a purchase request to the Helcim Commerce API
        purchase = bridge_oscar.PurchaseBridge(
            amount=total.incl_tax,
            token_id=token_id,
            card=card_details,
            billing_address=billing_address,
            save_token=save_token,
            django_user=self.request.user,
        )
        purchase_instance, token_instance = purchase.process()

        if token_instance:
            payment_source = token_instance.cc_type
        elif purchase_instance.cc_type:
            payment_source = purchase_instance.cc_type
        else:
            payment_source = 'credit card'

        # Record payment source and event
        source_type, _ = oscar_payment_models.SourceType.objects.get_or_create(
            name=payment_source
        )

        source = source_type.sources.model(
            source_type=source_type,
            amount_allocated=total.incl_tax,
            currency=total.currency,
        )
        self.add_payment_source(source)
        self.add_payment_event('Authorised', total.incl_tax)
