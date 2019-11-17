"""Models for the django-helcim application."""
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.db import models


class HelcimTransaction(models.Model):
    """Details of a single Helcim transaction."""
    id = models.UUIDField(
        default=uuid4,
        editable=False,
        primary_key=True,
        verbose_name='ID',
    )
    raw_request = models.CharField(
        blank=True,
        help_text='The raw request used for this transaction',
        max_length=1024,
        null=True,
    )
    raw_response = models.CharField(
        blank=True,
        help_text='The raw response returned for this transaction',
        max_length=1024,
        null=True,
    )
    transaction_success = models.BooleanField(
        help_text='Whether the transaction was successful or not',
    )
    response_message = models.CharField(
        blank=True,
        help_text='The response message with the API call',
        max_length=256,
        null=True,
    )
    notice = models.CharField(
        blank=True,
        help_text='Any error or warning messages from Helcim',
        max_length=128,
        null=True,
    )
    date_response = models.DateTimeField(
        help_text='The date and time of the API response',
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time this transaction was recorded in database',
    )
    TRANSACTION_TYPES = (
        ('s', 'purchase (sale)'),
        ('p', 'pre-authorization'),
        ('c', 'capture'),
        ('r', 'refund'),
    )
    transaction_type = models.CharField(
        choices=TRANSACTION_TYPES,
        help_text='The type of transaction',
        max_length=1,
    )
    transaction_id = models.PositiveIntegerField(
        blank=True,
        help_text='The Helcim Commerce transaction ID',
        null=True,
    )
    amount = models.DecimalField(
        blank=True,
        decimal_places=2,
        help_text='The transaction amount',
        max_digits=12,
        null=True,
    )
    currency = models.CharField(
        blank=True,
        help_text='The transaction currency',
        max_length=8,
        null=True,
    )
    cc_name = models.CharField(
        blank=True,
        help_text='The cardholder name',
        max_length=256,
        null=True,
    )
    cc_number = models.CharField(
        blank=True,
        help_text='The first four and last 4 digits of the credit card number',
        max_length=16,
        null=True,
    )
    cc_expiry = models.DateField(
        blank=True,
        help_text='The credit card expiry date',
        null=True,
    )
    cc_type = models.CharField(
        blank=True,
        help_text='The credit card type',
        max_length=32,
        null=True,
    )
    token = models.CharField(
        blank=True,
        help_text='The Helcim generated and stored credit card token',
        max_length=23,
        null=True,
    )
    token_f4l4 = models.CharField(
        blank=True,
        help_text='The first and last 4 digits of the credit card number',
        max_length=8,
        null=True,
    )
    avs_response = models.CharField(
        blank=True,
        help_text='The address verification response',
        max_length=1,
        null=True,
    )
    cvv_response = models.CharField(
        blank=True,
        help_text='The CVV verification response',
        max_length=1,
        null=True,
    )
    approval_code = models.CharField(
        blank=True,
        help_text='The transaction approval code',
        max_length=16,
        null=True,
    )
    order_number = models.CharField(
        blank=True,
        help_text='The Helcim order number',
        max_length=16,
        null=True,
    )
    customer_code = models.CharField(
        blank=True,
        help_text='The Helcim customer code',
        max_length=16,
        null=True,
    )

    class Meta:
        ordering = ('-date_response',)
        permissions = (
            (
                'helcim_transactions',
                'Can view and interact with Helcim transactions.'
            ),
        )

    def __str__(self):
        string_parts = [
            self.date_response,
            self.transaction_type,
        ]

        return ' - '.join(string_parts)

    @property
    def can_be_captured(self):
        """Check if this transaction can be captured."""
        return bool(
            self.transaction_success and self.transaction_type == 'p'
        )

    @property
    def can_be_refunded(self):
        """Check if this transaction can be refunded."""
        return all([
            self.transaction_success,
            (self.transaction_type == 's' or self.transaction_type == 'c'),
            (self.amount if self.amount else 0) > 0,
        ])

class HelcimToken(models.Model):
    """A Helcim card token."""
    id = models.UUIDField(
        default=uuid4,
        editable=False,
        primary_key=True,
        verbose_name='ID',
    )
    token = models.CharField(
        help_text='The Helcim card token number',
        max_length=23,
    )
    token_f4l4 = models.CharField(
        help_text='The first & last four digits of the credit card number',
        max_length=8
    )
    cc_name = models.CharField(
        blank=True,
        help_text='The cardholder name',
        max_length=256,
        null=True,
    )
    cc_expiry = models.DateField(
        blank=True,
        help_text='The credit card expiry date',
        null=True,
    )
    cc_type = models.CharField(
        blank=True,
        help_text='The credit card type',
        max_length=32,
        null=True,
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time this token was added to database',
    )
    customer_code = models.CharField(
        blank=True,
        help_text='The Helcim customer code',
        max_length=16,
        null=True,
    )
    django_user = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='helcim_tokens',
    )

    class Meta:
        permissions = (
            (
                'helcim_tokens',
                'Can view and interact with Helcim tokens.'
            ),
        )
        unique_together = (
            'token', 'token_f4l4', 'customer_code', 'django_user'
        )

    @property
    def display_as_card_number(self):
        """Displays token_f4l4 as a 16 character credit card number."""
        return '{}********{}'.format(self.token_f4l4[:4], self.token_f4l4[-4:])

    @property
    def get_credit_card_png(self):
        """Returns a path to a credit card .png for this token."""
        # Look for an image for this credit card
        if self.cc_type:
            image_path = 'helcim/{}.png'.format(self.cc_type.lower())

            # If found, return the path to the static file image
            if finders.find(image_path):
                return image_path

        # Return placeholder image
        return 'helcim/placeholder.png'

    @property
    def get_credit_card_svg(self):
        """Returns a path to a credit card .svg for this token."""
        # Look for an image for this credit card
        if self.cc_type:
            image_path = 'helcim/{}.svg'.format(self.cc_type.lower())

            # If found, return the path to the static file image
            if finders.find(image_path):
                return image_path

        # Return placeholder image
        return 'helcim/placeholder.svg'
