"""Admin settings for Helcim Commerce API transactions."""
from django.conf import settings
from django.contrib import admin

from helcim.models import HelcimTransaction

class HelcimTransactionAdmin(admin.ModelAdmin):
    """Admin class for the HelcimTransaction model."""
    MODEL_FIELDS = [
        'raw_request',
        'raw_response',
        'transaction_success',
        'response_message',
        'notice',
        'date_response',
        'date_created',
        'transaction_type',
        'transaction_id',
        'amount',
        'currency',
        'cc_name',
        'cc_number',
        'cc_expiry',
        'cc_type',
        'token',
        'avs_response',
        'cvv_response',
        'approval_code',
        'order_number',
        'customer_code',
    ]

    fields = MODEL_FIELDS

    readonly_fields = MODEL_FIELDS

    list_display = [
        'transaction_type',
        'date_response',
        'transaction_success',
        'amount',
        'customer_code',
    ]

# Only register the model if included in the settings
if hasattr(settings, 'HELCIM_INCLUDE_ADMIN') and settings.HELCIM_INCLUDE_ADMIN:
    admin.site.register(HelcimTransaction, HelcimTransactionAdmin)
