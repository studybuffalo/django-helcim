"""Tests for the Helcim URLs."""
from importlib import reload
import pytest

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from helcim import urls


@pytest.mark.django_db
def test_transaction_list_exists_at_desired_location(admin_client):
    """Tests that transaction list URL name works."""
    response = admin_client.get(reverse('helcim_transaction_list'))

    assert response.status_code == 200

@pytest.mark.django_db
def test_transaction_list_exists_at_desired_url(admin_client):
    """Tests that transaction list URL works."""
    response = admin_client.get('/transactions/')

    assert response.status_code == 200

@pytest.mark.django_db
def test_tokens_list_exists_at_desired_location(admin_client):
    """Tests that token list URL name works."""
    response = admin_client.get(reverse('helcim_token_list'))

    assert response.status_code == 200

@pytest.mark.django_db
def test_tokens_list_exists_at_desired_name(admin_client):
    """Tests that token list URL name works."""
    response = admin_client.get('/tokens/')

    assert response.status_code == 200

@override_settings(HELCIM_ENABLE_TOKEN_VAULT=False)
@pytest.mark.django_db
def test_token_urls_not_loaded_if_settings_are_false():
    """Tests that token list URL name works."""
    # Check that all URLs loaded initially
    assert len(urls.urlpatterns) == 4

    # Reload URLs and check that token URLs removed
    reload(urls)
    assert len(urls.urlpatterns) == 2

@override_settings()
@pytest.mark.django_db
def test_token_urls_not_loaded_if_settings_are_missing():
    """Tests that token list URL name works."""


    # Check that all URLs loaded initially
    reload(urls)
    assert len(urls.urlpatterns) == 4

    # Reload URLs and check that token URLs removed
    del settings.HELCIM_ENABLE_TOKEN_VAULT
    reload(urls)
    assert len(urls.urlpatterns) == 2
