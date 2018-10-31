"""URLs to integrate with django-oscar."""
from django.urls import path

from helcim import views

app_name = 'helcim'

urlpatterns = [
    path(
        'transactions/',
        views.TransactionListView.as_view(),
        name='transaction_list'
    ),
    path(
        'transactions/<id:transaction_id>/',
        views.TransactionDetailView.as_view(),
        name='transaction_detail'
    ),
]
