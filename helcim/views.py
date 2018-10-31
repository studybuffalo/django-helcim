"""Views for Helcim Commerce API transactions."""
from django.views import generic

from helcim import models


class TransactionListView(generic.ListView):
    """List of all transactions submitted made by django-helcim."""
    model = models.HelcimTransaction
    template_name = 'helcim/transaction_list.html'
    context_object_name = 'transactions'

class TransactionDetailView(generic.DetailView):
    """Details of a specific transaction made by django-helcim."""
    model = models.HelcimTransaction
    slug_field = 'id'
    slug_url_kwargs = 'transaction_id'
    template_name = 'helcim/transaction_detail.html'
    context_object_name = 'transaction'
