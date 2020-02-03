"""Views to test out django-helcim."""
from django.contrib import messages
from django.forms import HiddenInput
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from helcim.exceptions import ProcessingError, PaymentError
from helcim.gateway import Purchase
from helcim.models import HelcimTransaction, HelcimToken

from .forms import PaymentForm, HelcimjsPaymentForm


class BasePaymentView(FormView):
    """This view handles payment detail collection and processing.

        It is intended to be extended to allow the specific handling
        of the payment form, which may change depending on the use
        case.

        Will allow user to enter payment details, review the entered
        information on a confirmation page, then submit the payment.

        The GET call will return a page for the user to enter the
        payment details.

        THE POST calls use a ``process`` parameter to determine if
        a confirmation page needs to be displayed or if the payment
        shoudl be processed. This is done because you cannot transfer
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
        """Returns 404 error as this method is not implemented."""
        return self.render_details(request)

    def post(self, request, *args, **kwargs):
        """Handles POST requests and ensure proper handling.

            The 'process' POST argument is used to determine whether
            to render a confirmation page or process a payment.
        """
        print(request.POST)
        # Determine POST action and direct to proper function
        process = request.POST.get('process', None)

        # Need to add handling here to return back to processing page
        # on Helcim.js errors
        # Example Error on POST:
        # <QueryDict: {
        #   'csrfmiddlewaretoken': ['abc'],
        #   'response': ['0'],
        #   'responseMessage': ['Invalid Card Expiry - Card Has Expired'],
        #   'xml': ['<message>\r\n\t<response>0</response>\r\n\t<responseMessage>Invalid Card Expiry - Card Has Expired</responseMessage>\r\n</message>'],
        #   'cc_name': ['Myself'],
        #   'amount': ['1']
        # }>

        # Render the confirmation page
        if process:
            return self.process_payment(request)

        return self.render_confirmation(request)

    def render_details(self, request, **kwargs):
        """Renders the payment details form.

            If an error occurred during a POST, will render the
            payment form with any relevant errors.
        """
        context = self.get_context_data(**kwargs)

        # If error is present, there is POST data to include in form
        if 'error' in kwargs:
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

    def process_payment(self, request, **kwargs):
        """Moves forward with payment & subscription processing.

            This method needs to be extended to handle the unique
            requirements of each application.

            If forms are invalid will move back to payment details page
            for user to correct errors. This is only expected to happen
            if a user tampers with the hidden inputs.
        """
        raise NotImplementedError('This method must be overriden.')

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

class PaymentView(BasePaymentView):
    """This view handles a basic API purchase call."""
    form_class = PaymentForm
    template_details = 'example_app/payment_details.html'
    template_confirmation = 'example_app/payment_confirmation.html'

    def process_payment(self, request, **kwargs):
        """Moves forward with payment & subscription processing."""
        # Validate payment details again incase anything changed
        payment_form = self.form_class(request.POST)

        if payment_form.is_valid():
            # Format expiry for the Helcim API (MMYY)
            cc_expiry = '{}{}'.format(
                payment_form.cleaned_data['cc_expiry_month'],
                payment_form.cleaned_data['cc_expiry_year'][:-2],
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
                # NOTE: these types of errors are usually server-side
                # issues; you would not normally display them to a user
                messages.error(request, str(error))
            except PaymentError as error:
                # Format error response
                error_message = str(error).split('Helcim API request failed: ')

                messages.error(request, error_message[1])

            # If transaction was generated, payment was successful
            if transaction_success:
                # NOTE : you generally wouldn't want to transmit these
                # details as query parameters; this is just done to
                # simplify this example
                url = '{}?transaction={}&token={}'.format(
                    self.get_success_url(),
                    transaction.id,
                    token.id
                )
                return HttpResponseRedirect(url)

            # Payment unsuccessful, add message for confirmation page
            messages.error(request, 'Error processing payment')

        # Invalid form submission/payment - render payment details again
        kwargs['error'] = True

        return self.render_details(request, **kwargs)

class HelcimjsPaymentView(BasePaymentView):
    """This view handles an API purchase call with Helcim.js."""
    form_class = HelcimjsPaymentForm
    template_details = 'example_app/helcimjs_payment_details.html'
    template_confirmation = 'example_app/helcimjs_payment_confirmation.html'

    def process_payment(self, request, **kwargs):
        """Moves forward with payment & subscription processing."""
        # Validate payment details again incase anything changed
        payment_form = self.form_class(request.POST)

        if payment_form.is_valid():
            # Format expiry for the Helcim API (MMYY)
            cc_expiry = '{}{}'.format(
                payment_form.cleaned_data['cc_expiry_month'],
                payment_form.cleaned_data['cc_expiry_year'][:-2],
            )

            purchase = Purchase(
                save_token=True,
                amount=payment_form.cleaned_data['amount'],
                django_user=self.request.user,
                cc_name=payment_form.cleaned_data['cardholder_name'],
                cc_number=payment_form.cleaned_data['card_number'],
                cc_expiry=cc_expiry,
                cc_cvv=payment_form.cleaned_data['card_cvv'],
            )

            transaction_success = False

            try:
                transaction, token = purchase.process()
                transaction_success = bool(transaction)
            except ValueError as error:
                messages.error(request, str(error))
            except ProcessingError as error:
                # NOTE: these types of errors are usually server-side
                # issues; you would not normally display them to a user
                messages.error(request, str(error))
            except PaymentError as error:
                # Format error response
                error_message = str(error).split('Helcim API request failed: ')

                messages.error(request, error_message[1])

            if transaction_success:
                # NOTE : you generally wouldn't want to transmit these
                # details as query parameters; this is just done to
                # simplify this example
                url = '{}?transaction={}&token={}'.format(
                    self.get_success_url(),
                    transaction.id,
                    token.id
                )
                return HttpResponseRedirect(url)

            # Payment unsuccessful, add message for confirmation page
            messages.error(request, 'Error processing payment')

        # Invalid form submission/payment - render payment details again
        kwargs['error'] = True

        return self.render_details(request, **kwargs)

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

        return context
