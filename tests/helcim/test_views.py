"""Tests for the Helcim views."""
import pytest

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from helcim import models


@pytest.mark.django_db
def test_transaction_lists_template(admin_client):
    """Tests for proper HTML template."""
    response = admin_client.get(reverse('transaction_list'))

    assert (
        'helcim/transaction_list.html' in [t.name for t in response.templates]
    )

@pytest.mark.django_db
def test_403_if_not_authorized(client, django_user_model):
    """Tests transaction list redirect if inadequate permissions."""
    # Create user and login
    django_user_model.objects.create_user(username='user', password='password')
    client.login(username='user', password='password')

    response = client.get(reverse('transaction_list'))

    assert response.status_code == 403

@pytest.mark.django_db()
def test_200_if_authorized(client, django_user_model):
    """Tests transaction list doesn't redirect with permissions."""
    # Get the helcim_transactions permission
    content = ContentType.objects.get_for_model(models.HelcimTransaction)
    permission = Permission.objects.get(
        content_type=content, codename='helcim_transactions'
    )

    # Create the user and add permissions
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    user.user_permissions.add(permission)

    # Login and test response
    client.login(username='user', password='password')

    response = client.get(reverse('transaction_list'))

    assert response.status_code == 200
