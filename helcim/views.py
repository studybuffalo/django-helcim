"""Views for Helcim Commerce API transactions."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic

from helcim import models


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
