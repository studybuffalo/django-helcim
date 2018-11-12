"""Integration tests between Gateway and Model modules."""
# pylint: disable=missing-docstring
from datetime import datetime

import pytest

from django.contrib.auth import get_user_model
from django.test import override_settings

from helcim import exceptions as helcim_exceptions, gateway, models


@pytest.mark.django_db
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

@pytest.mark.django_db
def test_save_transaction_missing_required_field_handling():
    base = gateway.BaseRequest()
    base.response = {}

    try:
        base.save_transaction('s')
    except helcim_exceptions.DjangoError:
        assert True
    else:
        assert False

@pytest.mark.django_db
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

@override_settings(HELCIM_ENABLE_TOKEN_VAULT=True)
@pytest.mark.django_db
def test_save_token_saves_to_model():
    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
        'token_f4l4': '11119999',
    }
    base.save_token_to_vault()

    assert count + 1 == models.HelcimToken.objects.all().count()

@override_settings(HELCIM_ENABLE_TOKEN_VAULT=True)
@pytest.mark.django_db
def test_save_token_saves_to_model_with_user():
    user = get_user_model().objects.create_user(
        username='user', password='password'
    )
    count = models.HelcimToken.objects.all().count()

    base = gateway.BaseCardTransaction(save_token=True, django_user=user)
    base.response = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
        'token_f4l4': '11119999',
    }
    base.save_token_to_vault()

    assert count + 1 == models.HelcimToken.objects.all().count()
