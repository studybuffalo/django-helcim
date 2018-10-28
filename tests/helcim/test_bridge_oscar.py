"""Tests for the bridge_oscar module."""
# pylint: disable=missing-docstring
from datetime import datetime
from unittest.mock import patch

from oscar.apps.payment import exceptions as oscar_exceptions

from helcim import bridge_oscar, exceptions as helcim_exceptions


class MockPurchaseProcessValid():
    def process(self):
        return True

    def __init__(self, *args, **kwargs):
        pass

class MockPurchaseProcessHelcimError():
    def process(self):
        raise helcim_exceptions.HelcimError

    def __init__(self, *args, **kwargs):
        pass

class MockPurchaseProcessProcessingError():
    def process(self):
        raise helcim_exceptions.ProcessingError

    def __init__(self, *args, **kwargs):
        pass

class MockPurchaseProcessPaymentError():
    def process(self):
        raise helcim_exceptions.PaymentError

    def __init__(self, *args, **kwargs):
        pass

class MockCreditCard():
    def __init__(self, name=None, number=None, expiry=None, ccv=None):
        self.name = name
        self.number = number
        self.expiry_date = expiry
        self.ccv = ccv

@patch(
    'helcim.bridge_oscar.gateway.Purchase', MockPurchaseProcessValid
)
def test_purchase_valid():
    try:
        bridge_oscar.purchase('1', '2', MockCreditCard(), {'first_name': '3'})
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch(
    'helcim.bridge_oscar.gateway.Purchase',
    MockPurchaseProcessHelcimError
)
def test_purchase_helcim_error():
    try:
        bridge_oscar.purchase('1', '2', MockCreditCard())
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch(
    'helcim.bridge_oscar.gateway.Purchase',
    MockPurchaseProcessProcessingError
)
def test_purchase_processing_error():
    try:
        bridge_oscar.purchase('1', '2', MockCreditCard())
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch(
    'helcim.bridge_oscar.gateway.Purchase',
    MockPurchaseProcessPaymentError
)
def test_purchase_payment_error():
    try:
        bridge_oscar.purchase('1', '2', MockCreditCard())
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False

def test_remap_oscar_billing_address_patial():
    address = {
        'first_name': 'John',
        'last_name': 'Smith',
        'line1': '1234 Fake Street',
    }

    remapped = bridge_oscar.remap_oscar_billing_address(address)

    assert remapped['billing_contact_name'] == 'John Smith'
    assert remapped['billing_street_1'] == '1234 Fake Street'
    assert remapped['billing_street_2'] is None
    assert remapped['billing_city'] is None
    assert remapped['billing_province'] is None
    assert remapped['billing_postal_code'] is None
    assert remapped['billing_country'] is None
    assert remapped['billing_phone'] is None

def test_remap_oscar_billing_address_full():
    address = {
        'first_name': 'John',
        'last_name': 'Smith',
        'line1': '1234 Fake Street',
        'line2': '',
        'line3': '',
        'line4': 'Toronto',
        'state': 'Ontario',
        'postcode': 'O1O 1O1',
        'country': 'Canada',
        'phone_number': '123-456-7896',
    }

    remapped = bridge_oscar.remap_oscar_billing_address(address)

    assert len(remapped) == 8
    assert remapped['billing_contact_name'] == 'John Smith'
    assert remapped['billing_street_1'] == '1234 Fake Street'
    assert remapped['billing_street_2'] == ''
    assert remapped['billing_city'] == 'Toronto'
    assert remapped['billing_province'] == 'Ontario'
    assert remapped['billing_postal_code'] == 'O1O 1O1'
    assert remapped['billing_country'] == 'Canada'
    assert remapped['billing_phone'] == '123-456-7896'

def test_remap_oscar_billing_address_first_name_only():
    address = {
        'first_name': 'John',
    }

    remapped = bridge_oscar.remap_oscar_billing_address(address)

    assert remapped['billing_contact_name'] == 'John'

def test_remap_oscar_billing_address_last_name_only():
    address = {
        'last_name': 'Smith',
    }

    remapped = bridge_oscar.remap_oscar_billing_address(address)

    assert remapped['billing_contact_name'] == 'Smith'

def test_remap_oscar_billing_address_no_name():
    remapped = bridge_oscar.remap_oscar_billing_address({})

    assert remapped['billing_contact_name'] is None

def test_remap_oscar_credit_card_partial():
    card = MockCreditCard('John Smith')

    remapped = bridge_oscar.remap_oscar_credit_card(card)

    assert remapped['cc_name'] == 'John Smith'
    assert remapped['cc_number'] is None
    assert remapped['cc_expiry'] is None
    assert remapped['cc_cvv'] is None

def test_remap_oscar_credit_card_full():
    card = MockCreditCard('John Smith', '1234', datetime(2018, 1, 31), 100)

    remapped = bridge_oscar.remap_oscar_credit_card(card)

    assert len(remapped) == 4
    assert remapped['cc_name'] == 'John Smith'
    assert remapped['cc_number'] == '1234'
    assert remapped['cc_expiry'] == '0118'
    assert remapped['cc_cvv'] == 100
