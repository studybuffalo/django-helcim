"""Tests for the Helcim views."""
import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_transaction_lists_template(client):
    """Tests for proper HTML template."""
    response = client.get(reverse('transaction_list'))

    assert (
        'helcim/transaction_list.html' in [t.name for t in response.templates]
    )

@pytest.mark.django_db
def test_redirect_if_not_authorized():
    """Tests transaction list redirect if inadequate permissions."""
    pass

@pytest.mark.django_db
def test_no_redirect_if_authorized():
    """Tests transaction list redirect if inadequate permissions."""
    pass
