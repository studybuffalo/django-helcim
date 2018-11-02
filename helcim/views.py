"""Views for Helcim Commerce API transactions."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
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
    slug_field = 'id'
    slug_url_kwargs = 'transaction_id'
    permission_required = 'helcim.helcim_transactions'
    raise_exception = True
    context_object_name = 'transaction'
    template_name = 'helcim/transaction_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TransactionDetailView, self).get_context_data(**kwargs)
        # Checks settings for whether transaction should be read only
        context['show_form_buttons'] = getattr(
            settings, 'HELCIM_TRANSACTIONS_READ_ONLY', False
        )
        return context

    def post(self, request, *args, **kwargs):
        """Handles any capture and refund requests."""
        # Add setting to enable or disable this functionality
        read_only = getattr(
            settings, 'HELCIM_TRANSACTIONS_READ_ONLY', False
        )

        # Checks if this is setup as a read-only transaction
        if read_only:
            transaction = self.get_object()

            messages.error(
                self.request, 'Transactions cannot be modified'
            )
            return HttpResponseRedirect(
                reverse(
                    'transaction_list',
                    kwargs={'transaction_id': transaction.id}
                )
            )

        # Determines which action was submitted
        action = request.POST.get('action', None)

        if action == 'refund':
            return self.refund()

        if action == 'capture':
            return self.capture()

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
            messages.error(self.request, 'Unable to refund transaction.')
        else:
            messages.success(self.request, 'Transaction refunded')

        return HttpResponseRedirect(
            reverse(
                'transaction_details',
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
        except exceptions.RefundError:
            messages.error(self.request, 'Unable to capture transaction.')
        else:
            messages.success(self.request, 'Transaction captured')

        return HttpResponseRedirect(
            reverse(
                'transaction_details',
                kwargs={'transaction_id': transaction.id}
            )
        )
