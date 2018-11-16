"""URLs to integrate with django-oscar."""
# pylint: disable=line-too-long
from django.conf import settings
from django.conf.urls import url

from helcim import views

app_name = 'helcim'

urlpatterns = [
    url(
        r'^transactions/$',
        views.TransactionListView.as_view(),
        name='helcim_transaction_list'
    ),
    url(
        r'^transactions/(?P<transaction_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        views.TransactionDetailView.as_view(),
        name='helcim_transaction_detail'
    ),
]

# Only add these views if token vault is enabled
if getattr(settings, 'HELCIM_ENABLE_TOKEN_VAULT', False):
    urlpatterns += [
        url(
            r'^tokens/$',
            views.TokenListView.as_view(),
            name='helcim_token_list'
        ),
        url(
            r'^tokens/(?P<token_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
            views.TokenDeleteView.as_view(),
            name='helcim_token_delete'
        ),
    ]
