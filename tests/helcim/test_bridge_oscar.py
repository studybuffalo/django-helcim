"""Tests for the bridge_oscar module."""
# pylint: disable=missing-docstring

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

@patch(
    'helcim.bridge_oscar.gateway.Purchase', MockPurchaseProcessValid
)
def test_sale_valid():
    try:
        bridge_oscar.sale('1', 2, '1')
    except (oscar_exceptions.GatewayError, oscar_exceptions.PaymentError):
        assert False
    else:
        assert True

@patch(
    'helcim.bridge_oscar.gateway.Purchase',
    MockPurchaseProcessHelcimError
)
def test_sale_helcim_error():
    try:
        bridge_oscar.sale('1', 2, '1')
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch(
    'helcim.bridge_oscar.gateway.Purchase',
    MockPurchaseProcessProcessingError
)
def test_sale_processing_error():
    try:
        bridge_oscar.sale('1', 2, '1')
    except oscar_exceptions.GatewayError:
        assert True
    else:
        assert False

@patch(
    'helcim.bridge_oscar.gateway.Purchase',
    MockPurchaseProcessPaymentError
)
def test_sale_payment_error():
    try:
        bridge_oscar.sale('1', 2, '1')
    except oscar_exceptions.PaymentError:
        assert True
    else:
        assert False
