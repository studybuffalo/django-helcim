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

@pytest.mark.django_db
def test_helcim_token_minimal_model_creation():
    models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
    )

    assert models.HelcimToken.objects.all().count() == 1

@pytest.mark.django_db
def test_helcim_token_property_display_as_card_number():
    """Tests the display_as_card_number property."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
    )

    assert token.display_as_card_number == '1111********9999'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_png_mastercard():
    """Tests the get_credit_card_png property for a mastercard."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='mastercard',
    )

    assert token.get_credit_card_png == 'helcim/mastercard.png'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_png_visa():
    """Tests the get_credit_card_png property for a VISA."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='visa',
    )

    assert token.get_credit_card_png == 'helcim/visa.png'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_png_amex():
    """Tests the get_credit_card_png property for an AMEX."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='amex',
    )

    assert token.get_credit_card_png == 'helcim/amex.png'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_png_discover():
    """Tests the get_credit_card_png property for a discover."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='discover',
    )

    assert token.get_credit_card_png == 'helcim/discover.png'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_png_unkown():
    """Tests the get_credit_card_png property for an unknown card type."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='a',
    )

    assert token.get_credit_card_png == 'helcim/placeholder.png'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_png_missing():
    """Tests the get_credit_card_png property for a missing card type."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
    )

    assert token.get_credit_card_png == 'helcim/placeholder.png'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_svg_mastercard():
    """Tests the get_credit_card_svg property for a mastercard."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='mastercard',
    )

    assert token.get_credit_card_svg == 'helcim/mastercard.svg'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_svg_visa():
    """Tests the get_credit_card_svg property for a VISA."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='visa',
    )

    assert token.get_credit_card_svg == 'helcim/visa.svg'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_svg_amex():
    """Tests the get_credit_card_svg property for an AMEX."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='amex',
    )

    assert token.get_credit_card_svg == 'helcim/amex.svg'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_svg_discover():
    """Tests the get_credit_card_svg property for a discover."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='discover',
    )

    assert token.get_credit_card_svg == 'helcim/discover.svg'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_svg_unknown():
    """Tests the get_credit_card_svg property for an unknown card type."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
        cc_type='a',
    )

    assert token.get_credit_card_svg == 'helcim/placeholder.svg'

@pytest.mark.django_db
def test_helcim_token_property_get_credit_card_svg_missing():
    """Tests the get_credit_card_svg property for a missing card type."""
    token = models.HelcimToken.objects.create(
        token='abcdefghijklmnopqrstuvw',
        token_f4l4='11119999',
    )

    assert token.get_credit_card_svg == 'helcim/placeholder.svg'
