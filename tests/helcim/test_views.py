"""Tests for the Helcim views."""
from unittest.mock import patch

import pytest

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from django.test import override_settings
from django.urls import reverse

from helcim import exceptions, models


class MockRefund():
    """Mock of the Refund Object."""
    # pylint: disable=missing-docstring
    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def process(self):
        return True

class MockRefundError():
    """Mock of the Refund Object that returns RefundError."""
    # pylint: disable=missing-docstring
    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def process(self):
        raise exceptions.RefundError

class MockCapture():
    """Mock of the Capture Object."""
    # pylint: disable=missing-docstring
    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def process(self):
        return True

class MockCaptureError():
    """Mock of the Capture Objectthat returns PaymentError."""
    # pylint: disable=missing-docstring
    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def process(self):
        raise exceptions.PaymentError

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

@pytest.mark.django_db
def test_transaction_detail_get_context_read_only_missing(admin_client):
    """Tests that read only flag defaults to False."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['show_form_buttons'] is False

@override_settings(HELCIM_TRANSACTIONS_READ_ONLY=False)
@pytest.mark.django_db
def test_transaction_detail_get_context_read_only_false(admin_client):
    """Tests that read only flag is false when explicitly set."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['show_form_buttons'] is False

@override_settings(HELCIM_TRANSACTIONS_READ_ONLY=True)
@pytest.mark.django_db
def test_transaction_detail_get_context_read_only_true(admin_client):
    """Tests that read only flag is true when explicitly set."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['show_form_buttons'] is True

@pytest.mark.django_db
def test_transaction_detail_post_no_action(admin_client):
    """Tests POST handling when no action specified."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {}
    )

    assert response.status_code == 400
    assert response.content == b'Unrecognized transaction action'

@override_settings(HELCIM_TRANSACTIONS_READ_ONLY=True)
@pytest.mark.django_db
def test_transaction_detail_post_read_only_redirect(admin_client):
    """Tests POST handling when read only is True."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {},
    )
    assert response.status_code == 302

@override_settings(HELCIM_TRANSACTIONS_READ_ONLY=True)
@pytest.mark.django_db
def test_transaction_detail_post_read_only_message(admin_client):
    """Tests POST handling when read only is True."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'error'
    assert messages[0].message == 'Transactions cannot be modified'

@pytest.mark.django_db
@patch('helcim.gateway.Refund', MockRefund)
def test_transaction_detail_post_refund_action(admin_client):
    """Tests POST handling of valid Refund."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'refund'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'success'
    assert messages[0].message == 'Transaction refunded'

@pytest.mark.django_db
@patch('helcim.gateway.Refund', MockRefundError)
def test_transaction_refund_error(admin_client):
    """Tests handling of RefundErrors during refunds."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'refund'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'error'
    assert messages[0].message == 'Unable to refund transaction'

@pytest.mark.django_db
@patch('helcim.gateway.Capture', MockCapture)
def test_transaction_detail_post_capture_action(admin_client):
    """Tests POST handling of valid Capture."""
    # Create transaction
    transaction = create_transaction('p')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'capture'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'success'
    assert messages[0].message == 'Transaction captured'

@pytest.mark.django_db
@patch('helcim.gateway.Capture', MockCaptureError)
def test_transaction_capture_error(admin_client):
    """Tests handling of PaymentErrors during capture."""
    # Create transaction
    transaction = create_transaction('p')

    response = admin_client.post(
        reverse(
            'transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'capture'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'error'
    assert messages[0].message == 'Unable to capture transaction'
