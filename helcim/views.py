"""Views for Helcim Commerce API transactions."""
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from helcim import exceptions, models, gateway


class TransactionListView(PermissionRequiredMixin, generic.ListView):
    """List of all transactions submitted made by django-helcim."""
    model = models.HelcimTransaction
    permission_required = 'helcim.helcim_transactions'
    raise_exception = True
    context_object_name = 'transactions'
    template_name = 'helcim/transaction_list.html'

class TransactionDetailView(PermissionRequiredMixin, generic.DetailView):
    """Details of a specific transaction made by django-helcim."""
    model = models.HelcimTransaction
    pk_url_kwarg = 'transaction_id'
    permission_required = 'helcim.helcim_transactions'
    raise_exception = True
    context_object_name = 'transaction'
    template_name = 'helcim/transaction_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TransactionDetailView, self).get_context_data(**kwargs)

        # Check which actions are enabled
        settings = gateway.SETTINGS
        context['capture_enabled'] = settings['enable_transaction_capture']
        context['refund_enabled'] = settings['enable_transaction_refund']

        return context

    def post(self, request, *args, **kwargs):
        """Handles any capture and refund requests."""
        # Determines which action was submitted
        action = request.POST.get('action', None)

        if action == 'refund':
            if gateway.SETTINGS['enable_transaction_refund']:
                return self.refund()

            transaction = self.get_object()
            messages.error(self.request, 'Transactions cannot be refunded')

            return HttpResponseRedirect(
                reverse(
                    'helcim_transaction_detail',
                    kwargs={'transaction_id': transaction.id}
                )
            )

        if action == 'capture':
            if gateway.SETTINGS['enable_transaction_capture']:
                return self.capture()

            transaction = self.get_object()
            messages.error(self.request, 'Transactions cannot be captured')

            return HttpResponseRedirect(
                reverse(
                    'helcim_transaction_detail',
                    kwargs={'transaction_id': transaction.id}
                )
            )

        # Action not found - return bad request
        return HttpResponseBadRequest('Unrecognized transaction action')

    def refund(self):
        """Processes a refund transaction."""
        transaction = self.get_object()

        refund = gateway.Refund({
            'transaction_type': 'r',
            'amount': transaction.amount,
            'token': transaction.token,
            'token_f4l4': transaction.token_f4l4,
            'customer_code': transaction.customer_code,
        })

        try:
            refund.process()
        except exceptions.RefundError:
            messages.error(self.request, 'Unable to refund transaction')
        else:
            messages.success(self.request, 'Transaction refunded')

        return HttpResponseRedirect(
            reverse(
                'helcim_transaction_detail',
                kwargs={'transaction_id': transaction.id}
            )
        )

    def capture(self):
        """Processes a capture transaction."""
        transaction = self.get_object()

        capture = gateway.Capture({
            'transaction_type': 'c',
            'transaction_id': transaction.transaction_id,
        })

        try:
            capture.process()
        except exceptions.PaymentError:
            messages.error(self.request, 'Unable to capture transaction')
        else:
            messages.success(self.request, 'Transaction captured')

        return HttpResponseRedirect(
            reverse(
                'helcim_transaction_detail',
                kwargs={'transaction_id': transaction.id}
            )
        )

class TokenListView(PermissionRequiredMixin, generic.ListView):
    """List of all transactions submitted made by django-helcim."""
    model = models.HelcimToken
    permission_required = 'helcim.helcim_tokens'
    raise_exception = True
    context_object_name = 'tokens'
    template_name = 'helcim/token_list.html'

class TokenDeleteView(PermissionRequiredMixin, generic.DeleteView):
    """Allows deletion of a Helcim API token."""
    model = models.HelcimToken
    permission_required = 'helcim.helcim_tokens'
    raise_exception = True
    pk_url_kwarg = 'token_id'
    context_object_name = 'token'
    success_message = 'Token successfully deleted.'
    success_url = reverse_lazy('helcim_token_list')
    template_name = 'helcim/token_delete.html'

    def delete(self, request, *args, **kwargs):
        """Override delete to allow success message to be added."""
        messages.success(self.request, self.success_message)
        return super(TokenDeleteView, self).delete(request, *args, **kwargs)
