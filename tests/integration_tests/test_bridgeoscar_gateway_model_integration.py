"""Tests integrations between bridge_oscar-gateway-models."""
from datetime import date
from unittest.mock import patch

import pytest

from helcim import bridge_oscar, exceptions, models


def create_token(
        django_user=None, customer_code='1',
        token='abcdefghijklmnopqrstuvw', token_f4l4='11114444'
):
    """Creates a HelcimToken."""
    return models.HelcimToken.objects.create(
        token=token,
        token_f4l4=token_f4l4,
        customer_code=customer_code,
        django_user=django_user,
    )

class MockPostResponse():
    """Mocks a POST response from the Helcim Commerce API."""
    def __init__(self, url, data):
        self.text = """<?xml version="1.0"?>
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

@pytest.mark.django_db
def test_retrieve_token_details_valid(django_user_model):
    """Tests that retrieve_token_details properly populates dictionary."""
    # Create user and login
    django_user = django_user_model.objects.create_user(
        username='user', password='password'
    )

    # Create tokens to test against
    token_instance = create_token(django_user,)
    create_token(django_user, '1', 'zyxwvutsrqponmlkjihgfed', '99996666')

    # Retrieve details
    token_details = bridge_oscar.retrieve_token_details(
        token_instance.id, django_user
    )

    assert token_details['token'] == 'abcdefghijklmnopqrstuvw'
    assert token_details['token_f4l4'] == '11114444'
    assert token_details['customer_code'] == '1'

@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS',
    {'token_vault_identifier': 'django',}
)
@pytest.mark.django_db
def test_retrieve_token_details_valid_django_identifier(django_user_model):
    """Tests that function works for Django identifier."""
    # Create user and login
    django_user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    token_instance = create_token(django_user)

    token_details = bridge_oscar.retrieve_token_details(
        token_instance.id, django_user
    )

    assert token_details['token'] == 'abcdefghijklmnopqrstuvw'

@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS',
    {'token_vault_identifier': 'django',}
)
@pytest.mark.django_db
def test_retrieve_token_details_invalid_django_identifier(django_user_model):
    """Tests that function returns error for invalid django identifier."""
    # Create user and login
    django_user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    token_instance = create_token(django_user)

    try:
        bridge_oscar.retrieve_token_details(
            token_instance.id, '1'
        )
    except exceptions.ProcessingError as error:
        assert str(error) == (
            'Provided token does not exist for specified customer.'
        )

@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS',
    {'token_vault_identifier': 'helcim',}
)
@pytest.mark.django_db
def test_retrieve_token_details_valid_helcim_identifier(django_user_model):
    """Tests that function works for Helcim identifier."""
    # Create user and login
    django_user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    token_instance = create_token(django_user)

    token_details = bridge_oscar.retrieve_token_details(
        token_instance.id, '1'
    )

    assert token_details['token'] == 'abcdefghijklmnopqrstuvw'

@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS',
    {'token_vault_identifier': 'helcim',}
)
@pytest.mark.django_db
def test_retrieve_token_details_invalid_helcim_identifier(django_user_model):
    """Tests that function returns error for invalid helcim identifier."""
    # Create a token for testing
    django_user = django_user_model.objects.create_user(
        username='user', password='password'
    )
    token_instance = create_token(django_user)

    try:
        bridge_oscar.retrieve_token_details(
            token_instance.id, django_user
        )
    except exceptions.ProcessingError as error:
        assert str(error) == (
            'Unable to retrieve token details for specified customer.'
        )
    else:
        assert False

@pytest.mark.django_db
def test_retrieve_token_details_invalid_user(django_user_model):
    """Tests that retrieve_token_details properly populates dictionary."""
    # Create users
    django_user_1 = django_user_model.objects.create_user(
        username='user1', password='password'
    )
    django_user_2 = django_user_model.objects.create_user(
        username='user2', password='password'
    )
    token_instance = create_token(django_user_1)

    try:
        bridge_oscar.retrieve_token_details(
            token_instance.id, django_user_2
        )
    except exceptions.ProcessingError as error:
        assert str(error) == (
            'Unable to retrieve token details for specified customer.'
        )
    else:
        assert False

@pytest.mark.django_db
def test_retrieve_saved_tokens_valid(django_user_model):
    """Tests that retrieve_saved_tokens retrieves tokens properly."""
    # Create user and login
    django_user_1 = django_user_model.objects.create_user(
        username='user_1', password='password'
    )
    django_user_2 = django_user_model.objects.create_user(
        username='user_2', password='password'
    )

    # Create tokens
    create_token(django_user_1, '1', 'abcdefghijklmnopqrstuvw', '11114444')
    create_token(django_user_1, '1', 'zyxwvutsrqponmlkjihgfed', '99996666')
    create_token(django_user_2, '2', 'aaaaaaaaaaaaaaaaaaaaaaa', '22222222')

    # Retrieve tokens
    tokens = bridge_oscar.retrieve_saved_tokens(django_user_1)

    assert len(tokens) == 2
    assert tokens[0].customer_code == '1'
    assert tokens[1].customer_code == '1'
    assert tokens[0].token_f4l4 in ('11114444', '99996666')
    assert tokens[1].token_f4l4 in ('11114444', '99996666')
    assert tokens[0].token_f4l4 != tokens[1].token_f4l4

@patch(
    'helcim.bridge_oscar.gateway.requests.post',
    MockPostResponse
)
@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS',
    {
        'redact_all': False,
        'redact_cc_name': False,
        'redact_cc_number': False,
        'redact_cc_expiry': False,
        'redact_cc_type': False,
        'enable_token_vault': True,
        'token_vault_identifier': 'helcim',
    }
)
@pytest.mark.django_db
def test_purchase_bridge_valid_no_redaction():
    """Tests results of purchase bridge with no redaction."""
    credit_card = MockCreditCard(
        name='Test Person',
        number='1111222233334444',
        expiry=date(2025, 1, 31),
        ccv='100'
    )
    purchase = bridge_oscar.PurchaseBridge(
        amount='200.00',
        card=credit_card,
        billing_address={'first_name': 'Test Person'},
        save_token=True
    )
    transaction, token = purchase.process()

    # Check for expected transaction results
    assert isinstance(transaction, models.HelcimTransaction)
    assert transaction.transaction_id == 1111111
    assert transaction.cc_name == 'Test Person'
    assert 'amount=200.00' in transaction.raw_request
    assert 'cardHolderName=Test Person' in transaction.raw_request

    # Check for expected token details
    assert isinstance(token, models.HelcimToken)
    assert token.token == 'abcdefghijklmnopqrstuvw'
    assert token.token_f4l4 == '11114444'
    assert token.cc_name == 'Test Person'
    assert token.cc_expiry == date(2025, 1, 31)
    assert token.cc_type == 'MasterCard'
    assert token.customer_code == 'CST1000'
    assert token.django_user is None

@patch(
    'helcim.bridge_oscar.gateway.requests.post', MockPostResponse
)
@patch.dict(
    'helcim.bridge_oscar.gateway.SETTINGS',
    {
        'redact_all': True,
        'enable_token_vault': True,
        'token_vault_identifier': 'helcim',
    }
)
@pytest.mark.django_db
def test_purchase_bridge_valid_redact_sensitive_cc_data():
    """Tests results of purchase bridge with redaction."""
    credit_card = MockCreditCard(
        name='Test Person',
        number='1111222233334444',
        expiry=date(2025, 1, 1),
        ccv='100'
    )
    purchase = bridge_oscar.PurchaseBridge(
        amount='200.00',
        card=credit_card,
        billing_address={'first_name': 'Test Person'},
        save_token=True,
    )
    transaction, token = purchase.process()

    # Test transaction data saved and redacted
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
    assert (
        '<cardHolderName>REDACTED</cardHolderName>' in transaction.raw_response
    )
    assert '<cardNumber>REDACTED</cardNumber>' in transaction.raw_response
    assert '<expiryDate>REDACTED</expiryDate>' in transaction.raw_response
    assert '<cardType>REDACTED</cardType>' in transaction.raw_response
    assert '<cardToken>REDACTED</cardToken>' in transaction.raw_response

    # Test that token saved to vault properly
    assert token.token == 'abcdefghijklmnopqrstuvw'
    assert token.token_f4l4 == '11114444'
    assert token.cc_name is None
    assert token.cc_expiry is None
    assert token.cc_type == 'MasterCard'
    assert token.customer_code == 'CST1000'
    assert token.django_user is None
