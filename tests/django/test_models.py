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

@pytest.mark.django_db
def test_helcim_transaction_str():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='s',
    )

    assert str(transaction) == '2018-01-01 01:02:03 - s'

@pytest.mark.django_db
def test_helcim_transaction_can_be_captured_valid():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='p',
    )

    assert transaction.can_be_captured

@pytest.mark.django_db
def test_helcim_transaction_can_be_captured_invalid_success():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=False,
        date_response='2018-01-01 01:02:03',
        transaction_type='p',
    )

    assert transaction.can_be_captured is False

@pytest.mark.django_db
def test_helcim_transaction_can_be_captured_invalid_type():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='r',
    )

    assert transaction.can_be_captured is False

@pytest.mark.django_db
def test_helcim_transaction_can_be_refunded_valid_purchase():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='s',
        amount=1.00,
    )

    assert transaction.can_be_refunded

@pytest.mark.django_db
def test_helcim_transaction_can_be_refunded_valid_capture():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='c',
        amount=1.00,
    )

    assert transaction.can_be_refunded

@pytest.mark.django_db
def test_helcim_transaction_can_be_refunded_invalid_success():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=False,
        date_response='2018-01-01 01:02:03',
        transaction_type='s',
        amount=1.00,
    )

    assert transaction.can_be_refunded is False

@pytest.mark.django_db
def test_helcim_transaction_can_be_refunded_invalid_type():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='r',
        amount=1.00,
    )

    assert transaction.can_be_refunded is False

@pytest.mark.django_db
def test_helcim_transaction_can_be_refunded_invalid_amount():
    transaction = models.HelcimTransaction.objects.create(
        transaction_success=True,
        date_response='2018-01-01 01:02:03',
        transaction_type='s',
    )

    assert transaction.can_be_refunded is False
