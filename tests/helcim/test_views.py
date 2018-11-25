"""Tests for the Helcim views."""
from unittest.mock import patch

import pytest

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
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

def create_token(django_user=None):
    """Creates a HelcimToken."""
    return models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11114444',
        customer_code='1',
        django_user=django_user,
    )

@pytest.mark.django_db
def test_transaction_list_template(admin_client):
    """Tests for proper HTML template."""
    response = admin_client.get(reverse('helcim_transaction_list'))

    assert (
        'helcim/transaction_list.html' in [t.name for t in response.templates]
    )

@pytest.mark.django_db
def test_transaction_list_403_if_not_authorized(client, django_user_model):
    """Tests transaction list redirect if inadequate permissions."""
    # Create user and login
    django_user_model.objects.create_user(username='user', password='password')
    client.login(username='user', password='password')

    response = client.get(reverse('helcim_transaction_list'))

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

    response = client.get(reverse('helcim_transaction_list'))

    assert response.status_code == 200

@pytest.mark.django_db
def test_transaction_detail_template(admin_client):
    """Tests for proper HTML template."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
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
            'helcim_transaction_detail',
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
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.status_code == 200

@pytest.mark.django_db
def test_transaction_detail_get_context_capture_enabled_missing(admin_client):
    """Tests that capture_enabled flag defaults to False."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['capture_enabled'] is False

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_capture': False})
@pytest.mark.django_db
def test_transaction_detail_get_context_capture_enabled_false(admin_client):
    """Tests that capture_enabled flag is false when explicitly set."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['capture_enabled'] is False

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_capture': True})
@pytest.mark.django_db
def test_transaction_detail_get_context_capture_enabled_true(admin_client):
    """Tests that capture_enabled flag is true when explicitly set."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['capture_enabled'] is True

@pytest.mark.django_db
def test_transaction_detail_get_context_refund_enabled_missing(admin_client):
    """Tests that refund_enabled flag defaults to False."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['refund_enabled'] is False

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_refund': False})
@pytest.mark.django_db
def test_transaction_detail_get_context_refund_enabled_false(admin_client):
    """Tests that refund_enabled flag is false when explicitly set."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['refund_enabled'] is False

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_refund': True})
@pytest.mark.django_db
def test_transaction_detail_get_context_refund_enabled_true(admin_client):
    """Tests that refund_enabled flag is true when explicitly set."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.get(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        )
    )

    assert response.context['refund_enabled'] is True

@pytest.mark.django_db
def test_transaction_detail_post_no_action(admin_client):
    """Tests POST handling when no action specified."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {}
    )

    assert response.status_code == 400
    assert response.content == b'Unrecognized transaction action'

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_capture': False})
@pytest.mark.django_db
def test_transaction_detail_post_no_capture_redirect(admin_client):
    """Tests that view redirects on POST when capture not enabled."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'capture'},
    )
    assert response.status_code == 302

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_capture': False})
@pytest.mark.django_db
def test_transaction_detail_post_no_capture_message(admin_client):
    """Tests error message on POST when capture not enabled."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'capture'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'error'
    assert messages[0].message == 'Transactions cannot be captured'

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_refund': False})
@pytest.mark.django_db
def test_transaction_detail_post_no_refund_redirect(admin_client):
    """Tests that view redirects on POST when refund not enabled."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'refund'},
    )
    assert response.status_code == 302

@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_refund': False})
@pytest.mark.django_db
def test_transaction_detail_post_no_refund_message(admin_client):
    """Tests error message on POST when refund not enabled."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'refund'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'error'
    assert messages[0].message == 'Transactions cannot be refunded'

@pytest.mark.django_db
@patch('helcim.gateway.Refund', MockRefund)
@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_refund': True})
def test_transaction_detail_post_refund_action(admin_client):
    """Tests POST handling of valid Refund."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
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
@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_refund': True})
def test_transaction_refund_error(admin_client):
    """Tests handling of RefundErrors during refunds."""
    # Create transaction
    transaction = create_transaction('s')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
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
@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_capture': True})
def test_transaction_detail_post_capture_action(admin_client):
    """Tests POST handling of valid Capture."""
    # Create transaction
    transaction = create_transaction('p')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
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
@patch.dict('helcim.gateway.SETTINGS', {'enable_transaction_capture': True})
def test_transaction_capture_error(admin_client):
    """Tests handling of PaymentErrors during capture."""
    # Create transaction
    transaction = create_transaction('p')

    response = admin_client.post(
        reverse(
            'helcim_transaction_detail',
            kwargs={'transaction_id': transaction.id}
        ),
        {'action': 'capture'},
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'error'
    assert messages[0].message == 'Unable to capture transaction'

@pytest.mark.django_db
def test_token_list_template(admin_client):
    """Tests for proper HTML template for token list."""
    response = admin_client.get(reverse('helcim_token_list'))

    assert (
        'helcim/token_list.html' in [t.name for t in response.templates]
    )

@pytest.mark.django_db
def test_token_list_403_if_not_authorized(client, django_user_model):
    """Tests token list redirect if inadequate permissions."""
    # Create user and login
    django_user_model.objects.create_user(username='user', password='password')
    client.login(username='user', password='password')

    response = client.get(reverse('helcim_token_list'))

    assert response.status_code == 403

@pytest.mark.django_db
def test_token_list_200_if_authorized(client, django_user_model):
    """Tests tokens list doesn't redirect when user has permissions."""
    # Get the helcim_transactions permission
    content = ContentType.objects.get_for_model(models.HelcimToken)
    permission = Permission.objects.get(
        content_type=content, codename='helcim_tokens'
    )

    # Create the user and add permissions
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    user.user_permissions.add(permission)

    # Login and test response
    client.login(username='user', password='password')

    response = client.get(reverse('helcim_token_list'))

    assert response.status_code == 200

@pytest.mark.django_db
def test_token_delete_template(admin_client):
    """Tests for proper HTML template for token delete."""
    token = create_token()

    response = admin_client.get(reverse(
        'helcim_token_delete',
        kwargs={'token_id': token.id}
    ))

    assert (
        'helcim/token_delete.html' in [t.name for t in response.templates]
    )

@pytest.mark.django_db
def test_token_delete_403_if_not_authorized(client, django_user_model):
    """Tests token delete redirect if inadequate permissions."""
    token = create_token()

    # Create user and login
    django_user_model.objects.create_user(
        username='user', password='password'
    )
    client.login(username='user', password='password')

    response = client.get(reverse(
        'helcim_token_delete',
        kwargs={'token_id': token.id}
    ))

    assert response.status_code == 403

@pytest.mark.django_db
def test_token_delete_200_if_authorized(client, django_user_model):
    """Tests tokens delete doesn't redirect when user has permissions."""
    token = create_token()

    # Get the helcim_transactions permission
    content = ContentType.objects.get_for_model(models.HelcimToken)
    permission = Permission.objects.get(
        content_type=content, codename='helcim_tokens'
    )

    # Create the user and add permissions
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    user.user_permissions.add(permission)

    # Login and test response
    client.login(username='user', password='password')


    response = client.get(reverse(
        'helcim_token_delete',
        kwargs={'token_id': token.id}
    ))

    assert response.status_code == 200

@pytest.mark.django_db
def test_token_delete_post(admin_client):
    """Tests for token deletion on POST."""
    token = create_token()
    token_count = models.HelcimToken.objects.all().count()

    admin_client.post(reverse(
        'helcim_token_delete',
        kwargs={'token_id': token.id}
    ))

    assert token_count - 1 == models.HelcimToken.objects.all().count()

@pytest.mark.django_db
def test_token_delete_post_redirect_on_success(admin_client):
    """Tests for token deletion on POST."""
    token = create_token()

    response = admin_client.post(reverse(
        'helcim_token_delete',
        kwargs={'token_id': token.id}
    ))

    assert response.status_code == 302

@pytest.mark.django_db
def test_token_delete_post_message_on_success(admin_client):
    """Tests for token deletion on POST."""
    token = create_token()

    response = admin_client.post(
        reverse(
            'helcim_token_delete',
            kwargs={'token_id': token.id},
        ),
        follow=True
    )

    messages = [message for message in get_messages(response.wsgi_request)]

    assert response.status_code == 200
    assert messages[0].tags == 'success'
    assert messages[0].message == 'Token successfully deleted.'
