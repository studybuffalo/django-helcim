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
                    <cardToken>80defad45bae30e557da0e</cardToken>
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

# @patch(
#     'helcim.bridge_oscar.gateway.requests.post',
#     MockPostResponse
# )
# @override_settings(HELCIM_ENABLE_TOKEN_VAULT=True)
# @pytest.mark.django_db
# def test_purchase_bridge_valid_with_token():
#     """Tests that the purchase bridge properly creates models."""
#     credit_card = MockCreditCard(
#         name='Test Person',
#         number='1111222233334444',
#         expiry=datetime(2025, 1, 1),
#         ccv='100'
#     )
#     purchase = bridge_oscar.PurchaseBridge(
#         order_number='00001',
#         amount='200.00',
#         card=credit_card,
#         billing_address={'first_name': 'Test Person'},
#         save_token=True
#     )
#     transaction, token = purchase.process()

#     assert isinstance(transaction, models.HelcimTransaction)
#     assert transaction.transaction_id == 1111111
#     assert transaction.cc_name == 'Test Person'
#     assert transaction.raw_request == 'test'

#     assert isinstance(token, models.HelcimToken)

# @patch(
#     'helcim.bridge_oscar.gateway.requests.post',
#     MockPostResponse
# )
# @override_settings(HELCIM_ENABLE_TOKEN_VAULT=True)
# @pytest.mark.django_db
# def test_purchase_bridge_valid_redact_sensitive_information():
#     """Tests that the purchase bridge properly creates models."""
#     credit_card = MockCreditCard(
#         name='Test Person',
#         number='1111222233334444',
#         expiry=datetime(2025, 1, 1),
#         ccv='100'
#     )
#     purchase = bridge_oscar.PurchaseBridge(
#         order_number='00001',
#         amount='200.00',
#         card=credit_card,
#         billing_address={'first_name': 'Test Person'},
#         save_token=True
#     )
#     transaction, token = purchase.process()

#     assert isinstance(transaction, models.HelcimTransaction)
#     # accountID
#     # apiToken
#     # terminaID
#     # cardNumber
#     # card expiry
#     # card type
#     # token
#     assert transaction.transaction_id == 1111111
#     assert transaction.cc_name == 'Test Person'
#     assert transaction.raw_request == 'test'

#     assert isinstance(token, models.HelcimToken)
