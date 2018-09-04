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

    assert type(dictionary) is OrderedDict

def test_determine_payment_details_token():
    details = {
        'card_token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'token'

def test_determine_payment_details_customer():
    details = {
        'customer_code': 'CST1000',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'customer'

def test_determine_payment_details_cc():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'cc'

def test_determine_payment_details_mag_encrypted():
    details = {
        'cc_mag_encrypted': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'serial_number': 'SERIAL1230129912',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'mage'

def test_determine_payment_details_mag():
    details = {
        'cc_mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'mag'

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
        'card_token': 'abcdefghijklmnopqrstuvwxyz',
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'cc_mag_encrypted': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'serial_number': 'SERIAL1230129912',
        'cc_mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'token'

def determine_payment_details_customer_priority():
    details = {
        'customer_code': 'CST1000',
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'cc_mag_encrypted': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'serial_number': 'SERIAL1230129912',
        'cc_mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'customer'

def determine_payment_details_cc_priority():
    details = {
        'cc_number': '1234567890123456',
        'cc_expiry': '0125',
        'cc_mag_encrypted': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'serial_number': 'SERIAL1230129912',
        'cc_mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'cc'

def determine_payment_details_mag_encrypted_priority():
    details = {
        'cc_mag_encrypted': 'iscySW5ks7LeQQ8r4Tz7vb6el6QFpuQMbxGbh1==',
        'serial_number': 'SERIAL1230129912',
        'cc_mag': '%B45**********SENSITIVE*DATA******************01?2',
    }

    payment_type = gateway.determine_payment_details(details)

    assert payment_type == 'mage'
