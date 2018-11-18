"""Custom forms to override Django Oscar defaults."""
# pylint: disable=invalid-name, missing-docstring, protected-access
from django import forms
from django.conf import settings

from oscar.core.loading import get_class, get_model
from oscar.forms.mixins import PhoneNumberMixin


AbstractAddressForm = get_class('address.forms', 'AbstractAddressForm')
BillingAddress = get_model('order', 'BillingAddress')
Country = get_model('address', 'Country')

class BillingAddressForm(PhoneNumberMixin, AbstractAddressForm):
    """Overriding the BillingAddressForm."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_country_queryset()

        # Add a "save card" option if Token vault is enabled
        if getattr(settings, 'HELCIM_ENABLE_TOKEN_VAULT', False):
            self.fields['save_card'] = forms.BooleanField(
                label='Save credit card details to this account',
                required=False,
            )

    def set_country_queryset(self):
        self.fields['country'].queryset = Country._default_manager.all()

    class Meta:
        model = BillingAddress
        fields = [
            'title', 'first_name', 'last_name',
            'line1', 'line2', 'line3', 'line4',
            'state', 'postcode', 'country',
        ]
