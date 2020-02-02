"""Forms to test out django-helcim."""
from django import forms
from django.utils import timezone


class PaymentForm(forms.Form):
    """Example Payment Form."""
    MONTH_CHOICES = (
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
    YEAR_CHOICES = (
        (year, str(year)[2:]) for year in range(now.year, now.year + 50)
    )

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
        choices=MONTH_CHOICES,
        label='Month Expiry'
    )
    cc_expiry_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        label='Year Expiry'
    )
    amount = forms.DecimalField(
        decimal_places=4,
        initial='0.00',
        label='Amount',
        min_value=0,
    )
