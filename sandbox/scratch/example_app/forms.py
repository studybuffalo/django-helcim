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
    year_start = now.year
    year_end = year_start + 50
    year_choices = (
        (str(year)[2:], str(year)[2:]) for year in range(year_start, year_end)
    )

    return month_choices, year_choices

class HiddenInputCustomName(forms.HiddenInput):
    """Custom hidden input that lets you specify the widget's name attribute.

        This widget helps streamline communication with Helcim.js,
        which is expecting various camelCase names (as opposed to the
        usual snake_case names used in python) and the fact that some
        form elements shouldn't have names.
    """

    def get_context(self, name, value, attrs):
        context = super(HiddenInputCustomName, self).get_context(
            name, value, attrs
        )
        context['widget']['name'] = context['widget']['attrs'].get('name', '')

        return context

class PaymentForm(forms.Form):
    """Form to manage Helcim API purchase call."""
    month_choices, year_choices = get_expiry_choices()

    cc_number = forms.CharField(
        label='Credit Card Number',
        max_length=16,
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

    # Fields for user data entry
    django_cc_number = forms.CharField(
        label='Credit Card Number',
        max_length=16,
        min_length=13,
        required=False,
    )
    django_cc_expiry_month = forms.ChoiceField(
        choices=month_choices,
        label='Month Expiry',
        required=False,
    )
    django_cc_expiry_year = forms.ChoiceField(
        choices=year_choices,
        label='Year Expiry',
        required=False,
    )
    django_cc_cvv = forms.CharField(
        label='CVV',
        max_length=4,
        min_length=3,
        required=False,
    )
    django_cc_name = forms.CharField(
        label='Cardholder Name',
        max_length=256,
        required=False,
    )
    django_amount = forms.DecimalField(
        decimal_places=4,
        initial='0.00',
        label='Amount',
        min_value=0,
        required=False,
    )

    # Fields for Helcim.js processing
    helcim_cc_number = forms.CharField(
        max_length=16,
        min_length=13,
        required=False,
        widget=HiddenInputCustomName(
            attrs={'id': 'cardNumber', 'name': ''}
        ),
    )
    helcim_cc_expiry = forms.CharField(
        max_length=4,
        min_length=4,
        required=False,
        widget=HiddenInputCustomName(
            attrs={'id': 'cardExpiry', 'name': ''}
        ),
    )
    helcim_cc_cvv = forms.CharField(
        max_length=4,
        min_length=3,
        required=False,
        widget=HiddenInputCustomName(
            attrs={'id': 'cardCVV', 'name': ''}
        ),
    )
    helcim_cc_name = forms.CharField(
        max_length=256,
        required=False,
        widget=HiddenInputCustomName(
            attrs={'id': 'cardHolderName', 'name': ''}
        ),
    )
    helcim_amount = forms.CharField(
        initial='0.00',
        label='Amount',
        max_length=16,
        required=False,
        widget=HiddenInputCustomName(
            attrs={'id': 'amount', 'name': ''}
        ),
    )
