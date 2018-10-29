"""Tests for the Helcim models module."""
# pylint: disable=missing-docstring
import pytest

from helcim import models

@pytest.mark.django_db
def test_helcim_transaction_minimal_model_creation():
    models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='s',
    )

    assert models.HelcimTransaction.objects.all().count() == 1
