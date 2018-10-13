"""Configuration file for pytest."""
import os

import django


def pytest_configure():
    """Setups initial testing configuration."""
    # Setting up a Django instance for testing
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
    django.setup()
