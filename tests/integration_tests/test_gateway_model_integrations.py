"""Integration tests between Gateway and Model modules."""
# pylint: disable=missing-docstring
from datetime import datetime
from unittest.mock import patch

import pytest

from helcim import exceptions as helcim_exceptions, gateway, models


pytestmark = pytest.mark.django_db

def test_save_transaction_saves_to_model():
    count = models.HelcimTransaction.objects.all().count()

    base = gateway.BaseRequest()
    base.response = {
        'transaction_success': True,
        'transaction_date': datetime(2018, 1, 1).date(),
        'transaction_time': datetime(2018, 1, 1, 1, 2, 3).time(),
    }
    base.save_transaction('s')

    assert count + 1 == models.HelcimTransaction.objects.all().count()

def test_save_transaction_missing_required_field_handling():
    base = gateway.BaseRequest()
    base.response = {}

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

def test_save_transaction_invalid_data_type_handling():
    base = gateway.BaseRequest()
    base.response = {
        'transaction_success': True,
        'transaction_date': datetime(2018, 1, 1).date(),
        'transaction_time': datetime(2018, 1, 1, 1, 2, 3).time(),
        'transaction_id': 'a',
    }

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

@patch.dict('helcim.gateway.SETTINGS', {'enable_token_vault': True})
def test_save_token_saves_to_model(django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    base.save_token_to_vault()

    assert count + 1 == models.HelcimToken.objects.all().count()

@patch.dict('helcim.gateway.SETTINGS', {'enable_token_vault': True})
def test_save_token_saves_to_model_with_user(django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    base.save_token_to_vault()

    assert count + 1 == models.HelcimToken.objects.all().count()

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'associate_user': True},
)
def test_save_token_handles_duplicate_token_with_associate(django_user_model):
    user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    first_instance = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        customer_code='CST1000',
        django_user=user,
    )

    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    second_instance = base.save_token_to_vault()

    assert count == models.HelcimToken.objects.all().count()
    assert first_instance == second_instance

@patch.dict(
    'helcim.gateway.SETTINGS',
    {'enable_token_vault': True, 'associate_user': False},
)
def test_save_token_handles_duplicate_token_without_associate():
    first_instance = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        customer_code='CST1000',
        django_user=None,
    )

    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=None)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
    }
    second_instance = base.save_token_to_vault()

    assert count == models.HelcimToken.objects.all().count()
    assert first_instance == second_instance
