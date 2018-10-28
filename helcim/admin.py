"""Admin settings for Helcim Commerce API transactions."""
from django.contrib import admin

from helcim import models

@admin.register(models.HelcimTransaction)
class HelcimTransactionAdmin(admin.ModelAdmin):
    """Admin class for the HelcimTransaction model."""
    list_display = [
        'transaction_type',
        'date_response',
        'transaction_success',
        'amount',
        'customer_code',
    ]

    readonly_fields = [
        'raw_request',
        'raw_response',
        'transaction_success',
        'response_message',
        'notice',
        'date_response',
        'date_created',
        'transaction_type',
        'amount',
        'currency',
        'card_name',
        'card_number',
        'card_expiry',
        'card_type',
        'card_token',
        'avs_response',
        'cvv_response',
        'approval_code',
        'order_number',
        'customer_code',
    ]
