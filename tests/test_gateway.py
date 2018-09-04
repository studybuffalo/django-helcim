"""Tests for the gateway module."""
# pylint: disable=missing-docstring

from collections import OrderedDict
from unittest.mock import patch

from helcim import gateway

TEST_XML_RESPONSE = """<?xml version="1.0"?>
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
            <amount>100.00</amount>
            <currency>CAD</currency>
            <cardNumber>5454********5454</cardNumber>
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

@patch('helcim.gateway.requests.post')
def test_post_returns_dictionary(mock_post):
    mock_post.return_value = TEST_XML_RESPONSE

    dictionary = gateway.post('', {})

    assert isinstance(dictionary, OrderedDict)


@patch('helcim.gateway.requests.post')
def test_purchase(mock_post):
    mock_post.return_value = TEST_XML_RESPONSE

    api_details = {
        'url': 'https://www.test.com',
        'account_id': '12345678',
        'token': 'abcdefg',
        'terminal_id': '98765432',
    }
    amount = 100.00
    payment_details = {
        'customer_code': 'CST1000',
    }

    response = gateway.purchase(api_details, amount, payment_details)

    assert isinstance(response, OrderedDict)


def test_determine_payment_details_token():
    details = {
        'token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
        'token_f4l4': '11119999',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 3
    assert payment['cardToken'] == details['token']
    assert payment['customerCode'] == details['customer_code']
    assert payment['cardF4L4'] == details['token_f4l4']

def test_determine_payment_details_token_with_f4l4_skip():
    details = {
        'token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
        'token_f4l4_skip': True,
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 3
    assert payment['cardToken'] == details['token']
    assert payment['customerCode'] == details['customer_code']
    assert payment['cardF4L4Skip'] == 1

def test_determine_payment_details_token_f4l4_missing_error():
    details = {
        'token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
    }

    try:
        gateway.determine_payment_details(details)
    except ValueError:
        assert True
    else:
        assert False

def test_determine_payment_details_customer():
    details = {
        'customer_code': 'CST1000',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 1
    assert payment['customerCode'] == details['customer_code']

def test_determine_payment_details_cc():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 2
    assert payment['cardNumber'] == details['cc_number']
    assert payment['cardexpiry'] == details['cc_expiry']

def test_determine_payment_details_cc_with_details():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'cc_name': 'Test Person',
        'cc_cvv': '123',
        'cc_address': '100 Fake Street',
        'cc_postal_code': 'T1T 1T1',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 6
    assert payment['cardNumber'] == details['cc_number']
    assert payment['cardexpiry'] == details['cc_expiry']
    assert payment['cardHolderName'] == details['cc_name']
    assert payment['cardCVV'] == details['cc_cvv']
    assert payment['cardHolderAddress'] == details['cc_address']
    assert payment['cardHolderPostalCode'] == details['cc_postal_code']

def test_determine_payment_details_mag_encrypted():
    details = {
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 2
    assert payment['cardMagEnc'] == details['mag_enc']
    assert payment['serialNumber'] == details['mag_enc_serial_number']

def test_determine_payment_details_mag():
    details = {
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 1
    assert payment['cardMag'] == details['mag']

def test_determine_payment_details_value_error():
    details = {}

    try:
        gateway.determine_payment_details(details)
    except ValueError:
        assert True
    else:
        assert False

def determine_payment_details_token_priority():
    details = {
        'token': 'abcdefghijklmnopqrstuvwxyz',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 3
    assert 'cardToken' in payment

def determine_payment_details_customer_priority():
    details = {
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 1
    assert 'customerCode' in payment

def determine_payment_details_cc_priority():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 2
    assert 'cardNumber' in payment

def determine_payment_details_mag_encrypted_priority():
    details = {
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment = gateway.determine_payment_details(details)

    assert len(payment) == 2
    assert 'cardMagEnc' in payment
