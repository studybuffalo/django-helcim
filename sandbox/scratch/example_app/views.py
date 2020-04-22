"""Views to test out django-helcim."""
from django.contrib import messages
from django.forms import HiddenInput
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from helcim.exceptions import ProcessingError, PaymentError
from helcim.gateway import Purchase, HelcimJSResponse
from helcim.mixins import HelcimJSMixin
from helcim.models import HelcimTransaction, HelcimToken

from .forms import PaymentForm, HelcimjsPaymentForm


class PaymentView(FormView):
    """This view handles a basic API purchase call.

        This view is an example of how an application that requires
        payment processing (e.g. a subscription service, an online
        store) may function. The django-helcim specific details will
        be found in the post and process_payment methods. The majority
        of the remaining methods are meant to represent a generic
        service that requires payment processing.

        The GET call will return a page for the user to enter the
        payment details.

        The POST calls use a ``process`` parameter to determine if
        a confirmation page needs to be displayed or if the payment
        should be processed. This is done because you cannot transfer
        POST data securely through a redirection.
    """
    confirmation = False
    form_class = PaymentForm
    success_url = 'example:complete'
    template_details = 'example_app/payment_details.html'
    template_confirmation = 'example_app/payment_confirmation.html'

    def get_template_names(self):
        """Returns the proper template name based on payment stage."""
        conf_templates = [self.template_confirmation]
        det_templates = [self.template_details]

        return conf_templates if self.confirmation else det_templates

    def get_success_url(self, **kwargs): # pylint: disable=arguments-differ
        """Returns the success URL."""
        return reverse_lazy(self.success_url, kwargs=kwargs)

    def get(self, request, *args, **kwargs):
        """Returns the initial payment processing form."""
        return self.render_details(request)

    def post(self, request, *args, **kwargs):
        """Handles POST requests and ensure proper handling.

            The 'back' POST argument is used to signal that the user
            wants to return the payment details page.

            The 'process' POST argument is used to determine whether
            to render a confirmation page or process a payment.
        """
        # Determine POST action and direct to proper function

        # If "back" is present, return the payment details form again
        if request.POST.get('back', None):
            kwargs['back'] = True
            self.confirmation = False
            return self.render_details(request, **kwargs)

        # Process the payment
        if request.POST.get('process', None):
            return self.process_payment(request)

        # Render the confirmation page
        return self.render_confirmation(request)

    def render_details(self, request, **kwargs):
        """Renders the payment details form.

            If an error occurred during a POST, will render the
            payment form with any relevant errors.

            If "back" is present, will navigate back to payment
            details page.
        """
        context = self.get_context_data(**kwargs)

        # If there is form data already present, use it for inital form data
        # Error is added if there are processing errors during a POST
        # "back" is added when user navigates back from confirmation view
        if 'error' in kwargs or 'back' in kwargs:
            payment_form = self.form_class(request.POST)
        else:
            payment_form = self.form_class()

        context['form'] = payment_form

        return self.render_to_response(context)

    def render_confirmation(self, request, **kwargs):
        """Renders a confirmation page before processing payment.

            If forms are invalid will return to the payment details
            view for user to correct errors.
        """
        # Retrive form details
        payment_form = self.form_class(request.POST)

        # Validate form submission
        if payment_form.is_valid():
            # Sets confirmation to True to retrieve proper template
            self.confirmation = True

            # Updates Context with updated form that hides all the
            # user input via the HiddenInput Widget (this reduces the
            # risk of the user accidentally editing payment details at
            # this stage)
            context = self.get_context_data(**kwargs)
            context['form'] = self.hide_form(payment_form)

            return self.render_to_response(context)

        # Invalid form submission - render payment details again
        kwargs['error'] = True

        return self.render_details(request, **kwargs)

    def hide_form(self, form):
        """Replaces form widgets with hidden inputs.
            Parameters:
                form (obj): A form instance.
            Returns:
                obj: The modified form instance.
        """
        for _, field in form.fields.items():
            field.widget = HiddenInput()

        return form

    def process_payment(self, request, **kwargs):
        """Moves forward with payment & subscription processing."""
        # Validate payment details again incase anything changed
        payment_form = self.form_class(request.POST)

        if payment_form.is_valid():
            # Format expiry for the Helcim API (MMYY)
            cc_expiry = '{}{}'.format(
                payment_form.cleaned_data['cc_expiry_month'],
                payment_form.cleaned_data['cc_expiry_year'],
            )

            purchase = Purchase(
                save_token=True,
                amount=payment_form.cleaned_data['amount'],
                django_user=self.request.user,
                cc_name=payment_form.cleaned_data['cc_name'],
                cc_number=payment_form.cleaned_data['cc_number'],
                cc_expiry=cc_expiry,
                cc_cvv=payment_form.cleaned_data['cc_cvv'],
            )

            transaction_success = False

            try:
                transaction, token = purchase.process()
                transaction_success = bool(transaction)
            except ValueError as error:
                messages.error(request, str(error))
            except ProcessingError as error:
                # NOTE: ProcessingErrors are usually server-side errors;
                # you would not normally display them to a user
                messages.error(request, str(error))
            except PaymentError as error:
                # Format error response; the Helcim API prepends
                # "Helcim API request failed: " to the error. We strip that
                # out here to give a better user facing error
                error_message = str(error).split('Helcim API request failed: ')

                messages.error(request, error_message[1])

            # If transaction was generated, payment was successful
            if transaction_success:
                # NOTE: you generally wouldn't want to transmit these
                # details as query parameters; this is just done to
                # simplify this sandbox example
                url = '{}?transaction_type={}&transaction={}&token={}'.format(
                    self.get_success_url(),
                    'api',
                    transaction.id,
                    token.id,
                )
                return HttpResponseRedirect(url)

        # Invalid form submission/payment - render payment details again
        kwargs['error'] = True

        return self.render_details(request, **kwargs)

class HelcimJSPaymentView(HelcimJSMixin, FormView):
    """This view handles an API purchase call with Helcim.js.

        This view is an example of how an application that requires
        payment processing (e.g. a subscription service, an online
        store) may function. The django-helcim specific details will
        be found in the post and process_payment methods. The majority
        of the remaining methods are meant to represent a generic
        service that requires payment processing.

        When making a POST call, Helcim.js will intercept the request
        and direct it to the Helcim API server directly. This prevents
        any transmission of sensitive data to your servers and reduces
        your PCI Compliance requirements. These views and templates for
        this behaviour.

        The GET call will return a page for the user to enter the
        payment details.

        When the user "submits" their payment, there is client-side
        processing to generate the Confirmation view. This will enable
        confirmation display and allow an actual POST to occur.
        Helcim.js will intercept the request at this point. If the
        request is valid, the user token and response details will be
        saved; if it is invalid, the user will be directed back to the
        payment details view to review and correct the noted error(s).
    """
    form_class = HelcimjsPaymentForm
    success_url = 'example:complete'
    template_name = 'example_app/helcimjs_payment_details.html'

    def get_success_url(self, **kwargs): # pylint: disable=arguments-differ
        """Returns the success URL."""
        return reverse_lazy(self.success_url, kwargs=kwargs)

    def post(self, request, *args, **kwargs):
        """Handles remaining processing after Helcim.js processing."""
        response = HelcimJSResponse(
            response=request.POST, save_token=True, django_user=request.user
        )

        if response.is_valid():
            # NOTE: the type of transaction made by Helcim.js is determined by
            # the Helcim.js configuration. You will need to decide on the
            # proper "record" method to use for your situation.
            transaction, token = response.record_purchase()

            # NOTE: you generally wouldn't want to transmit these
            # details as query parameters; this is just done to
            # simplify this sandbox example
            url = '{}?transaction_type={}&transaction={}&token={}'.format(
                self.get_success_url(),
                'helcimjs',
                transaction.id,
                token.id,
            )
            return HttpResponseRedirect(url)

        # Invalid form submission/payment - render payment details again
        # TODO: add some basic initial data to the form
        form = self.get_form()

        return self.form_invalid(form)

class SuccessView(TemplateView):
    """View to display additional details on successful transaction."""
    template_name = 'example_app/complete.html'

    def get_context_data(self, **kwargs):
        """Adds additional context from the query parameters."""
        context = super().get_context_data(**kwargs)

        # Tries and retrieve the relevant model instances
        # This will silently fail if it can't find the instance
        transaction_id = self.request.GET.get('transaction', None)
        token_id = self.request.GET.get('token', None)

        if transaction_id:
            transaction = HelcimTransaction.objects.filter(
                id=transaction_id
            ).first()

        if token_id:
            token = HelcimToken.objects.filter(id=token_id).first()

        context['transaction'] = transaction
        context['token'] = token

        # Determine if this was an API or Helcim.js transaction
        transaction_type = self.request.GET.get('transaction_type', None)
        context['transaction_type'] = transaction_type

        return context
