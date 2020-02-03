"""Context processors for the sandbox app.

    These are intended to streamline some configuration of the
    sandbox site to allow quicker and easier testing.
"""
from django.conf import settings

def helcim_processor(request):
    """Allows you to set the Helcim.js details in the .env file."""
    return {
        'helcimjs_url': settings.HELCIM_HELCIMJS_URL,
        'helcimjs_token': settings.HELCIM_HELCIMJS_TOKEN,
    }
