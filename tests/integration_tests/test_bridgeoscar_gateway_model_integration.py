"""Tests integrations between bridge_oscar-gateway-models."""
from datetime import datetime
from unittest.mock import patch

import pytest

#from django.contrib.auth import get_user_model
from django.test import override_settings

from helcim import bridge_oscar, models


class MockPostResponse():
    """Mocks a POST response from the Helcim Commerce API."""
    def __init__(self, url, data):
        self.content = """<?xml version="1.0"?>
            <message>
                <response>1</response>
                <responseMessage>APPROVED</responseMessage>
                <notice></notice>
                <transaction>
                    <transactionId>1111111</transactionId>
                    <type>purchase</type>
                    <date>2018-01-01</date>
                    <time>12:00:00</time>
                    <cardHolderName>Test Person</cardHolderName>
                    <amount>200.00</amount>
                    <currency>CAD</currency>
                    <cardNumber>1111********4444</cardNumber>
                    <cardToken>abcdefghijklmnopqrstuvw</cardToken>
                    <expiryDate>0125</expiryDate>
                    <cardType>MasterCard</cardType>
                    <avsResponse>X</avsResponse>
                    <cvvResponse>M</cvvResponse>
                    <approvalCode>T6E1ST</approvalCode>
                    <orderNumber>INV1000</orderNumber>
                    <customerCode>CST1000</customerCode>
                </transaction>
            </message>
            """
        self.status_code = 200
        self.url = url
        self.data = data

class MockCreditCard():
    """A mock of the Oscar credit card object."""
    def __init__(self, name=None, number=None, expiry=None, ccv=None):
        self.name = name
        self.number = number
        self.expiry_date = expiry
        self.ccv = ccv

@patch(
    'helcim.bridge_oscar.gateway.requests.post',
    MockPostResponse
)
@override_settings(HELCIM_REDACT_ALL=False, HELCIM_ENABLE_TOKEN_VAULT=True)
@pytest.mark.django_db
def test_purchase_bridge_valid_with_token():
    """Tests that the purchase bridge properly creates models."""
    credit_card = MockCreditCard(
        name='Test Person',
        number='1111222233334444',
        expiry=datetime(2025, 1, 1),
        ccv='100'
    )
    purchase = bridge_oscar.PurchaseBridge(
        order_number='00001',
        amount='200.00',
        card=credit_card,
        billing_address={'first_name': 'Test Person'},
        save_token=True
    )
    transaction, token = purchase.process()

    # Spot check to see that things were generated properly
    assert isinstance(transaction, models.HelcimTransaction)
    assert transaction.transaction_id == 1111111
    assert transaction.cc_name == 'Test Person'
    assert 'orderNumber=00001' in transaction.raw_request
    assert 'amount=200.00' in transaction.raw_request
    assert 'cardHolderName=Test Person' in transaction.raw_request

    assert isinstance(token, models.HelcimToken)
    assert token.token == 'abcdefghijklmnopqrstuvw'
    assert token.token_f4l4 == '11114444'
    assert token.customer_code == 'CST1000'
    assert token.django_user is None

@patch(
    'helcim.bridge_oscar.gateway.requests.post',
    MockPostResponse
)
@override_settings(HELCIM_REDACT_ALL=True, HELCIM_ENABLE_TOKEN_VAULT=True)
@pytest.mark.django_db
def test_purchase_bridge_valid_redact_sensitive_cc_data():
    """Tests that the purchase bridge properly creates models."""
    credit_card = MockCreditCard(
        name='Test Person',
        number='1111222233334444',
        expiry=datetime(2025, 1, 1),
        ccv='100'
    )
    purchase = bridge_oscar.PurchaseBridge(
        order_number='00001',
        amount='200.00',
        card=credit_card,
        billing_address={'first_name': 'Test Person'},
        save_token=True
    )
    transaction, _ = purchase.process()

    assert transaction.cc_name is None
    assert transaction.cc_number is None
    assert transaction.cc_expiry is None
    assert transaction.cc_type is None
    assert transaction.token is None
    assert 'accountId=REDACTED' in transaction.raw_request
    assert 'apiToken=REDACTED' in transaction.raw_request
    assert 'terminalId=REDACTED' in transaction.raw_request
    assert 'cardHolderName=REDACTED' in transaction.raw_request
    assert 'cardNumber=REDACTED' in transaction.raw_request
    assert 'cardExpiry=REDACTED' in transaction.raw_request

# TODO: Add ability to Redact CCV
# TODO: CONFIRM ALL SENSITIVE FIELDS CAN BE REDACTED
# TODO: Make sure redaction can work when field is missing
