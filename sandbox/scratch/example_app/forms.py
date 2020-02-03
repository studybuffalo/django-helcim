"""Forms to test out django-helcim."""
from django import forms
from django.utils import timezone


def get_expiry_choices():
    """Generates proper tuples for month and year expiry choices."""
    month_choices = (
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
    )

    # Assembles years for the next 50 years (the longest likely expiry)
    now = timezone.now()
    year_choices = (
        (year, str(year)[2:]) for year in range(now.year, now.year + 50)
    )

    return month_choices, year_choices

class TextInputCustomName(forms.TextInput):
    """Custom input that lets you specify the widget's name attribute.

        This widget helps streamline communication with Helcim.js,
        which is expecting various camelCase names (as opposed to the
        usual snake_case names used in python).
    """

    def get_context(self, name, value, attrs):
        context = super(TextInputCustomName, self).get_context(
            name, value, attrs
        )
        context['widget']['name'] = context['widget']['attrs'].get('name', '')

        return context

class PaymentForm(forms.Form):
    """Form to manage Helcim API purchase call."""
    month_choices, year_choices = get_expiry_choices()

    cc_number = forms.CharField(
        label='Credit Card Number',
        max_length=19,
        min_length=13,
    )
    cc_name = forms.CharField(
        label='Cardholder Name',
        max_length=128,
    )
    cc_cvv = forms.CharField(
        label='CVV',
        max_length=4,
        min_length=3,
    )
    cc_expiry_month = forms.ChoiceField(
        choices=month_choices,
        label='Month Expiry'
    )
    cc_expiry_year = forms.ChoiceField(
        choices=year_choices,
        label='Year Expiry'
    )
    amount = forms.DecimalField(
        decimal_places=4,
        initial='0.00',
        label='Amount',
        min_value=0,
    )

class HelcimjsPaymentForm(forms.Form):
    """Form to manage Helcim API purchase call using Helcim.js.

        Fields in this form are not required because the Helcim.js
        scripts will capture the POST call and modify various details.
        This configuration will allow you to still use a Django form
        for validation and templating, while making use of the
        Helcim.js features.
    """
    month_choices, year_choices = get_expiry_choices()

    cc_number = forms.CharField(
        label='Credit Card Number',
        max_length=19,
        required=False,
        widget=TextInputCustomName(attrs={'id': 'cardNumber', 'name': ''})
    )
    cc_expiry_month = forms.ChoiceField(
        choices=month_choices,
        label='Month Expiry',
        required=False,
        widget=forms.Select(attrs={'id': 'cardExpiryMonth'})
    )
    cc_expiry_year = forms.ChoiceField(
        choices=year_choices,
        label='Year Expiry',
        required=False,
        widget=forms.Select(attrs={'id': 'cardExpiryYear'})
    )
    cc_cvv = forms.CharField(
        label='CVV',
        max_length=4,
        required=False,
        widget=TextInputCustomName(attrs={'id': 'cardCVV', 'name': ''})
    )
    cc_name = forms.CharField(
        label='Name on Card',
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'id': 'cardHolderName'})
    )
    card_token = forms.CharField(
        label='Card Token',
        max_length=23,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'cardToken'})
    )
    customer_code = forms.CharField(
        label='Customer Code',
        max_length=16,
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'customerCode'})
    )
    amount = forms.DecimalField(
        decimal_places=4,
        initial='0.00',
        label='Amount',
        min_value=0,
    )
