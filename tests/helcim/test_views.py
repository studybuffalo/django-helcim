"""Tests for the Helcim views."""
import pytest

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from helcim import models

def create_transaction(transaction_type):
    """Creates a HelcimTransaction."""
    return models.HelcimTransaction.objects.create(
        raw_request='a',
        raw_response='b',
        transaction_success=True,
        response_message='c',
        notice='d',
        date_response='2018-01-01 01:01:01',
        date_created='2018-02-02 02:02:02',
        transaction_type=transaction_type,
        transaction_id='1',
        amount='2.2',
        currency='CAD',
        cc_name='e',
        cc_number='1111********9999',
        cc_expiry='2028-01-31',
        cc_type='MasterCard',
        token='f',
        token_f4l4='11119999',
        avs_response='g',
        cvv_response='h',
        approval_code='i',
        order_number='j',
        customer_code='k',
    )

@pytest.mark.django_db
def test_transaction_list_template(admin_client):
    """Tests for proper HTML template."""
    response = admin_client.get(reverse('transaction_list'))

    assert (
        'helcim/transaction_list.html' in [t.name for t in response.templates]
    )

@pytest.mark.django_db
def test_transaction_list_403_if_not_authorized(client, django_user_model):
    """Tests transaction list redirect if inadequate permissions."""
    # Create user and login
    django_user_model.objects.create_user(username='user', password='password')
    client.login(username='user', password='password')

    response = client.get(reverse('transaction_list'))

    assert response.status_code == 403

@pytest.mark.django_db
def test_transaction_list_200_if_authorized(client, django_user_model):
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

@pytest.mark.django_db
def test_transaction_detail_template(admin_client):
    """Tests for proper HTML template."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert (
        'helcim/transaction_detail.html' in [
            t.name for t in response.templates
        ]
    )

@pytest.mark.django_db
def test_transaction_detail_403_if_not_authorized(client, django_user_model):
    """Tests transaction detail redirect if inadequate permissions."""
    # Create transaction
    transaction = create_transaction('s')

    # Create user and login
    django_user_model.objects.create_user(username='user', password='password')
    client.login(username='user', password='password')

    response = client.get(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.status_code == 403

@pytest.mark.django_db()
def test_transaction_detail_200_if_authorized(client, django_user_model):
    """Tests transaction detail doesn't redirect with permissions."""
    # Create transaction
    transaction = create_transaction('s')

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

    response = client.get(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.status_code == 200
