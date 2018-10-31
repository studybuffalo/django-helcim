"""Integration tests between Gateway and Model modules."""
# pylint: disable=missing-docstring
from datetime import datetime

import pytest

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
