"""URLs to integrate with django-oscar."""
# pylint: disable=line-too-long
from django.conf.urls import url

from helcim import views

app_name = 'helcim'

urlpatterns = [
    url(
        r'^transactions/$',
        views.TransactionListView.as_view(),
        name='transaction_list'
    ),
    url(
        r'^transactions/(?P<transaction_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        views.TransactionDetailView.as_view(),
        name='transaction_detail'
    ),
]
