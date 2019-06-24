"""Tests for the Helcim URLs."""
from importlib import reload
from unittest.mock import patch
import pytest

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

@pytest.mark.django_db
def test_token_urls_not_loaded_if_settings_are_false():
    """Tests that token list URL name works."""
    # Check correct number of URLs when vault disabled
    with patch.dict('helcim.gateway.SETTINGS', {'enable_token_vault': False}):
        reload(urls)
        assert len(urls.urlpatterns) == 2

    # Check correct number of URLs when vault enabled
    # NB: Need to reload URLs in this order otherwise tests bleed into others
    with patch.dict('helcim.gateway.SETTINGS', {'enable_token_vault': True}):
        reload(urls)
        assert len(urls.urlpatterns) == 4
