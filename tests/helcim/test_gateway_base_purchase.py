"""Tests for the gateway module."""
# pylint: disable=missing-docstring, protected-access
from helcim import gateway


API_DETAILS = {
    'url': 'https://www.test.com',
    'account_id': '12345678',
    'token': 'abcdefg',
    'terminal_id': '98765432',
}

def test_determine_purchase_payment_details_token():
    details = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
        'token_f4l4': '11119999',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 3
    assert purchase.cleaned['token'] == details['token']
    assert purchase.cleaned['customer_code'] == details['customer_code']
    assert purchase.cleaned['token_f4l4'] == details['token_f4l4']

def test_determine_payment_details_token_with_f4l4_skip():
    details = {
        'token': 'abcdefghijklmnopqrstuvw',
        'customer_code': 'CST1000',
        'token_f4l4_skip': True,
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 3
    assert purchase.cleaned['token'] == details['token']
    assert purchase.cleaned['customer_code'] == details['customer_code']
    assert purchase.cleaned['token_f4l4_skip'] == 1

def test_determine_payment_details_token_f4l4_missing_error():
    details = {
        'token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
    }

    try:
        purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
        purchase.validate_fields()
        purchase.determine_payment_details()
    except ValueError:
        assert True
    else:
        assert False

def test_determine_payment_details_customer():
    details = {
        'customer_code': 'CST1000',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 1
    assert purchase.cleaned['customer_code'] == details['customer_code']

def test_determine_payment_details_cc():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 2
    assert purchase.cleaned['cc_number'] == details['cc_number']
    assert purchase.cleaned['cc_expiry'] == details['cc_expiry']

def test_determine_payment_details_cc_with_details():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'cc_name': 'Test Person',
        'cc_cvv': '123',
        'cc_address': '100 Fake Street',
        'cc_postal_code': 'T1T 1T1',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 6
    assert purchase.cleaned['cc_number'] == details['cc_number']
    assert purchase.cleaned['cc_expiry'] == details['cc_expiry']
    assert purchase.cleaned['cc_name'] == details['cc_name']
    assert purchase.cleaned['cc_cvv'] == details['cc_cvv']
    assert purchase.cleaned['cc_address'] == details['cc_address']
    assert purchase.cleaned['cc_postal_code'] == details['cc_postal_code']

def test_determine_payment_details_mag_encrypted():

    details = {
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 2
    assert purchase.cleaned['mag_enc'] == details['mag_enc']
    assert (
        purchase.cleaned['mag_enc_serial_number']
        == details['mag_enc_serial_number']
    )

def test_determine_payment_details_mag():
    details = {
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 1
    assert purchase.cleaned['mag'] == details['mag']

def test_determine_payment_details_value_error():
    details = {}

    try:
        purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
        purchase.validate_fields()
        purchase.determine_payment_details()
    except ValueError:
        assert True
    else:
        assert False

def test_determine_payment_details_token_priority():
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

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 3
    assert 'token' in purchase.cleaned

def test_determine_payment_details_customer_priority():
    details = {
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 1
    assert 'customer_code' in purchase.cleaned

def test_determine_payment_details_cc_priority():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 2
    assert 'cc_number' in purchase.cleaned

def test_determine_payment_details_mag_encrypted_priority():
    details = {
        'mag_enc': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'mag_enc_serial_number': 'SERIAL1230129912',
        'mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    purchase = gateway.BasePurchase(api_details=API_DETAILS, **details)
    purchase.validate_fields()
    purchase.determine_payment_details()

    assert len(purchase.cleaned) == 2
    assert 'mag_enc' in purchase.cleaned
