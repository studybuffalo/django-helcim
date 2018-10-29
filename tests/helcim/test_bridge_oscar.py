"""Tests for the bridge_oscar module."""
# pylint: disable=missing-docstring
from datetime import datetime
from unittest.mock import patch

from oscar.apps.payment import exceptions as oscar_exceptions

from helcim import bridge_oscar, exceptions as helcim_exceptions


class MockProcessValid():
    def process(self):
        return True

    def __init__(self, *args, **kwargs):
        pass

class MockProcessHelcimError():
    def process(self):
        raise helcim_exceptions.HelcimError

    def __init__(self, *args, **kwargs):
        pass

class MockProcessProcessingError():
    def process(self):
        raise helcim_exceptions.ProcessingError

    def __init__(self, *args, **kwargs):
        pass

class MockProcessPaymentError():
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

def test_base_card_bridge_formats_details():
    transaction = bridge_oscar.BaseCardTransactionBridge(
        '1', '2', MockCreditCard(), {'first_name': '3'}
    )

    assert 'order_number' in transaction.transaction_details
    assert transaction.transaction_details['order_number'] == '1'
    assert 'amount' in transaction.transaction_details
    assert transaction.transaction_details['amount'] == '2'
    assert 'cc_name' in transaction.transaction_details
    assert 'cc_number' in transaction.transaction_details
    assert 'cc_expiry' in transaction.transaction_details
    assert 'cc_cvv' in transaction.transaction_details
    assert 'billing_contact_name' in transaction.transaction_details
    assert transaction.transaction_details['billing_contact_name'] == '3'
    assert 'billing_street_1' in transaction.transaction_details
    assert 'billing_street_2' in transaction.transaction_details
    assert 'billing_city' in transaction.transaction_details
    assert 'billing_province' in transaction.transaction_details
    assert 'billing_postal_code' in transaction.transaction_details
    assert 'billing_country' in transaction.transaction_details
    assert 'billing_phone' in transaction.transaction_details

def test_base_card_bridge_formats_details_without_billing_address():
    transaction = bridge_oscar.BaseCardTransactionBridge(
        '1', '2', MockCreditCard()
    )

    assert len(transaction.transaction_details) == 6
    assert 'order_number' in transaction.transaction_details
    assert transaction.transaction_details['order_number'] == '1'
    assert 'amount' in transaction.transaction_details
    assert transaction.transaction_details['amount'] == '2'
    assert 'cc_name' in transaction.transaction_details
    assert 'cc_number' in transaction.transaction_details
    assert 'cc_expiry' in transaction.transaction_details
    assert 'cc_cvv' in transaction.transaction_details

@patch('helcim.bridge_oscar.gateway.Purchase', MockProcessValid)
def test_purchase_bridge_valid():
    purchase = bridge_oscar.PurchaseBridge(
        '1', '2', MockCreditCard(), {'first_name': '3'}
    )

    try:
        purchase.process()
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch('helcim.bridge_oscar.gateway.Purchase', MockProcessHelcimError)
def test_purchase_bridge_helcim_error():
    purchase = bridge_oscar.PurchaseBridge(
        '1', '2', MockCreditCard()
    )

    try:
        purchase.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Purchase', MockProcessProcessingError)
def test_purchase_bridge_processing_error():
    purchase = bridge_oscar.PurchaseBridge(
        '1', '2', MockCreditCard()
    )

    try:
        purchase.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Purchase', MockProcessPaymentError)
def test_purchase_bridge_payment_error():
    purchase = bridge_oscar.PurchaseBridge(
        '1', '2', MockCreditCard()
    )

    try:
        purchase.process()
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Preauthorize', MockProcessValid)
def test_preauthorize_bridge_valid():
    preauth = bridge_oscar.PreauthorizeBridge(
        '1', '2', MockCreditCard()
    )

    try:
        preauth.process()
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch('helcim.bridge_oscar.gateway.Preauthorize', MockProcessHelcimError)
def test_preauthorize_bridge_helcim_error():
    preauth = bridge_oscar.PreauthorizeBridge(
        '1', '2', MockCreditCard()
    )

    try:
        preauth.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Preauthorize', MockProcessProcessingError)
def test_preauthorize_bridge_processing_error():
    preauth = bridge_oscar.PreauthorizeBridge(
        '1', '2', MockCreditCard()
    )

    try:
        preauth.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Preauthorize', MockProcessPaymentError)
def test_preauthorize_bridge_payment_error():
    preauth = bridge_oscar.PreauthorizeBridge(
        '1', '2', MockCreditCard()
    )

    try:
        preauth.process()
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Refund', MockProcessValid)
def test_refund_bridge_valid():
    refund = bridge_oscar.RefundBridge(
        '1', '2', MockCreditCard()
    )

    try:
        refund.process()
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch('helcim.bridge_oscar.gateway.Refund', MockProcessHelcimError)
def test_refund_bridge_helcim_error():
    refund = bridge_oscar.RefundBridge(
        '1', '2', MockCreditCard()
    )

    try:
        refund.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Refund', MockProcessProcessingError)
def test_refund_bridge_processing_error():
    refund = bridge_oscar.RefundBridge(
        '1', '2', MockCreditCard()
    )

    try:
        refund.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Refund', MockProcessPaymentError)
def test_refund_bridge_payment_error():
    refund = bridge_oscar.RefundBridge(
        '1', '2', MockCreditCard()
    )

    try:
        refund.process()
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Verification', MockProcessValid)
def test_verification_bridge_valid():
    verification = bridge_oscar.VerificationBridge(
        '1', '2', MockCreditCard()
    )

    try:
        verification.process()
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch('helcim.bridge_oscar.gateway.Verification', MockProcessHelcimError)
def test_verification_bridge_helcim_error():
    verification = bridge_oscar.VerificationBridge(
        '1', '2', MockCreditCard()
    )

    try:
        verification.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Verification', MockProcessProcessingError)
def test_verification_bridge_processing_error():
    verification = bridge_oscar.VerificationBridge(
        '1', '2', MockCreditCard()
    )

    try:
        verification.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Verification', MockProcessPaymentError)
def test_verification_bridge_payment_error():
    verification = bridge_oscar.VerificationBridge(
        '1', '2', MockCreditCard()
    )

    try:
        verification.process()
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Capture', MockProcessValid)
def test_capture_bridge_valid():
    capture = bridge_oscar.CaptureBridge(1)

    try:
        capture.process()
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch('helcim.bridge_oscar.gateway.Capture', MockProcessHelcimError)
def test_capture_bridge_helcim_error():
    capture = bridge_oscar.CaptureBridge(1)

    try:
        capture.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Capture', MockProcessProcessingError)
def test_capture_bridge_processing_error():
    capture = bridge_oscar.CaptureBridge(1)

    try:
        capture.process()
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch('helcim.bridge_oscar.gateway.Capture', MockProcessPaymentError)
def test_capture_bridge_payment_error():
    capture = bridge_oscar.CaptureBridge(1)

    try:
        capture.process()
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False
