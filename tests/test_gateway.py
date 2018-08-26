from collections import OrderedDict
from unittest.mock import Mock, patch

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
