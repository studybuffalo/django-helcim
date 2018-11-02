"""Tests for the Helcim URLs."""
import pytest

from django.urls import reverse

@pytest.mark.django_db
def test_transaction_list_exists_at_desired_location(admin_client):
    """Tests that transaction list URL name works."""
    response = admin_client.get(reverse('transaction_list'))

    assert response.status_code == 200

# @pytest.mark.django_db
# def test_transaction_list_exists_with_namespace(admin_client):
#     """Tests that transaction list URL name works."""
#     response = admin_client.get(reverse('helcim:transaction_list'))

#     assert response.status_code == 200

@pytest.mark.django_db
def test_transaction_list_exists_at_desired_url(admin_client):
    """Tests that transaction list URL works."""
    response = admin_client.get('/transactions/')

    assert response.status_code == 200
