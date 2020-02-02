"""URLs for the example app."""
# pylint: disable=line-too-long
from django.conf.urls import url
from django.views.generic import TemplateView

from .views import PaymentView, SuccessView


app_name = 'example'

urlpatterns = [
    url(r'payment/basic/$', PaymentView.as_view(), name='payment_basic'),
    url(r'payment/helcim-js/$', PaymentView.as_view(), name='payment_helcim_js'),
    url(r'complete/$', SuccessView.as_view(), name='complete'),
    url(
        r'^$',
        TemplateView.as_view(template_name='example_app/index.html'),
        name='home',
    ),
]
