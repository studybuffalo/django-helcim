"""Admin settings for Helcim Commerce API transactions."""
from django.conf import settings
from django.contrib import admin

from helcim.models import HelcimTransaction, HelcimToken

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
        'token_f4l4',
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
class HelcimTokenAdmin(admin.ModelAdmin):
    """Admin class for the HelcimToken model."""
    MODEL_FIELDS = [
        'token',
        'token_f4l4',
        'date_added',
        'customer_code',
        'django_user'
    ]

    fields = MODEL_FIELDS

    readonly_fields = MODEL_FIELDS

    list_display = [
        'date_added',
        'django_user',
        'customer_code',
        'token',
        'token_f4l4',
    ]

# Only register admin models if enabled in settings
if getattr(settings, 'HELCIM_INCLUDE_ADMIN', False):
    admin.site.register(HelcimTransaction, HelcimTransactionAdmin)
    admin.site.register(HelcimToken, HelcimTokenAdmin)
