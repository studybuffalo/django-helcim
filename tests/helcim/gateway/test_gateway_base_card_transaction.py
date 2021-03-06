"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access
from helcim import gateway


API_DETAILS = {
    'url': 'https://www.test.com',
    'account_id': '12345678',
    'token': 'abcdefg',
    'terminal_id': '98765432',
}

def test_determine_card_details_token():
    details = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
        'token_f4l4': '11119999',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 3
    assert transaction.cleaned['token'] == details['token']
    assert transaction.cleaned['customer_code'] == details['customer_code']
    assert transaction.cleaned['token_f4l4'] == details['token_f4l4']

def test_determine_card_details_token_with_f4l4_skip():
    details = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
        'token_f4l4_skip': True,
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 3
    assert transaction.cleaned['token'] == details['token']
    assert transaction.cleaned['customer_code'] == details['customer_code']
    assert transaction.cleaned['token_f4l4_skip'] == 1

def test_determine_card_details_token_f4l4_missing_error():
    details = {
        'token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
    }

    try:
        transaction = gateway.BaseCardTransaction(
            api_details=API_DETAILS, **details
        )
        transaction.validate_fields()
        transaction.determine_card_details()
    except ValueError:
        assert True
    else:
        assert False

def test_determine_card_details_customer():
    details = {
        'customer_code': 'CST1000',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 1
    assert transaction.cleaned['customer_code'] == details['customer_code']

def test_determine_card_details_cc():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 2
    assert transaction.cleaned['cc_number'] == details['cc_number']
    assert transaction.cleaned['cc_expiry'] == details['cc_expiry']

def test_determine_card_details_cc_with_details():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'cc_name': 'Test Person',
        'cc_cvv': '123',
        'cc_address': '100 Fake Street',
        'cc_postal_code': 'T1T 1T1',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 6
    assert transaction.cleaned['cc_number'] == details['cc_number']
    assert transaction.cleaned['cc_expiry'] == details['cc_expiry']
    assert transaction.cleaned['cc_name'] == details['cc_name']
    assert transaction.cleaned['cc_cvv'] == details['cc_cvv']
    assert transaction.cleaned['cc_address'] == details['cc_address']
    assert transaction.cleaned['cc_postal_code'] == details['cc_postal_code']

def test_determine_card_details_mag_encrypted():

    details = {
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 2
    assert transaction.cleaned['mag_enc'] == details['mag_enc']
    assert (
        transaction.cleaned['mag_enc_serial_number']
        == details['mag_enc_serial_number']
    )

def test_determine_card_details_mag():
    details = {
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 1
    assert transaction.cleaned['mag'] == details['mag']

def test_determine_card_details_value_error():
    details = {}

    try:
        transaction = gateway.BaseCardTransaction(
            api_details=API_DETAILS, **details
        )
        transaction.validate_fields()
        transaction.determine_card_details()
    except ValueError:
        assert True
    else:
        assert False

def test_determine_card_details_token_priority():
    details = {
        'token': 'abcdefghijklmnopqrstuvw',
        'token_f4l4': '11119999',
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 3
    assert 'token' in transaction.cleaned

def test_determine_card_details_customer_priority():
    details = {
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 1
    assert 'customer_code' in transaction.cleaned

def test_determine_card_details_cc_priority():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 2
    assert 'cc_number' in transaction.cleaned

def test_determine_card_details_mag_encrypted_priority():
    details = {
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    transaction = gateway.BaseCardTransaction(
        api_details=API_DETAILS, **details
    )
    transaction.validate_fields()
    transaction.determine_card_details()

    assert len(transaction.cleaned) == 2
    assert 'mag_enc' in transaction.cleaned
