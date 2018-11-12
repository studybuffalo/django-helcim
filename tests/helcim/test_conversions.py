"""Tests for the conversions module."""
# pylint: disable=missing-docstring, protected-access

from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

from helcim import conversions

# *_API_FIELDS being mocked to allow proper testing of validation
MOCK_TO_API_FIELDS_DECIMAL = {
    'amount': conversions.Field('amount', 'c', 10, 100),
}

MOCK_TO_API_FIELDS_STRING = {
    'cc_cvv': conversions.Field('cardCVV', 's', 3, 4),
}

MOCK_TO_API_FIELDS_INTEGER = {
    'product_id': conversions.Field('productId', 'i', 1, 100),
}

MOCK_TO_API_FIELDS_BOOLEAN = {
    'test': conversions.Field('test', 'b'),
}

MOCK_TO_API_FIELDS_ALL = {
    'amount': conversions.Field('amount', 'c', 10, 100),
    'cc_cvv': conversions.Field('cardCVV', 's', 3, 4),
    'product_id': conversions.Field('productId', 'i', 1, 100),
    'test': conversions.Field('test', 'b'),
}

MOCK_TO_API_FIELDS_INVALID = {
    'invalid': conversions.Field('value', 't'),
}

MOCK_FROM_API_FIELDS_DECIMAL = {
    'amount': conversions.Field('amount', 'c'),
}

MOCK_FROM_API_FIELDS_STRING = {
    'cardNumber': conversions.Field('cc_number', 's'),
}

MOCK_FROM_API_FIELDS_INTEGER = {
    'transactionId': conversions.Field('transaction_id', 'i'),
}

MOCK_FROM_API_FIELDS_BOOLEAN = {
    'availability': conversions.Field('availability', 'b'),
}

MOCK_FROM_API_FIELDS_DATE = {
    'date': conversions.Field('transaction_date', 'd'),
}

MOCK_FROM_API_FIELDS_TIME = {
    'time': conversions.Field('transaction_time', 't')
}

MOCK_FROM_API_FIELDS_ALL = {
    'amount': conversions.Field('amount', 'c'),
    'cardNumber': conversions.Field('cc_number', 's'),
    'transactionId': conversions.Field('transaction_id', 'i'),
    'availability': conversions.Field('availability', 'b'),
    'date': conversions.Field('transaction_date', 'd'),
    'time': conversions.Field('transaction_time', 't')
}

class InvalidField():
    def __init__(self, field_name, field_type):
        self.field_name = field_name
        self.field_type = field_type

MOCK_FROM_API_FIELDS_INVALID = {
    'invalid': InvalidField('field', 'x')
}

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_STRING)
def test_validate_request_fields_string_valid():
    details = {
        'cc_cvv': '123'
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'cc_cvv' in cleaned
    assert cleaned['cc_cvv'] == details['cc_cvv']

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_STRING)
def test_validate_request_fields_string_min():
    details = {
        'cc_cvv': '12'
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "cc_cvv field length too short."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_STRING)
def test_validate_request_fields_string_max():
    details = {
        'cc_cvv': '12345'
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "cc_cvv field length too long."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_INTEGER)
def test_validate_request_fields_integer_valid():
    details = {
        'product_id': 100
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'product_id' in cleaned
    assert cleaned['product_id'] == details['product_id']

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_INTEGER)
def test_validate_request_fields_integer_min():
    details = {
        'product_id': 0
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "product_id field value too small."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_INTEGER)
def test_validate_request_fields_integer_max():
    details = {
        'product_id': 101
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "product_id field value too large."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_DECIMAL)
def test_validate_request_fields_decimal_valid():
    details = {
        'amount': Decimal('50.00')
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'amount' in cleaned
    assert cleaned['amount'] == details['amount']

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_DECIMAL)
def test_validate_request_fields_decimal_min():
    details = {
        'amount': Decimal('1.00')
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "amount field value too small."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_DECIMAL)
def test_validate_request_fields_decimal_max():
    details = {
        'amount': Decimal('200.00')
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "amount field value too large."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_BOOLEAN)
def test_validate_request_fields_boolean_true():
    details = {
        'test': True
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'test' in cleaned
    assert cleaned['test'] == 1

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_BOOLEAN)
def test_validate_request_fields_boolean_false():
    details = {
        'test': False
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'test' in cleaned
    assert cleaned['test'] == 0

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_ALL)
def test_validate_request_fields_all_valid():
    """Tests that validations works for all fields at once."""
    details = {
        'cc_cvv': '123',
        'product_id': 100,
        'amount': Decimal('50.00'),
        'test': True,
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'cc_cvv' in cleaned
    assert cleaned['cc_cvv'] == details['cc_cvv']
    assert 'product_id' in cleaned
    assert cleaned['product_id'] == details['product_id']
    assert 'amount' in cleaned
    assert cleaned['amount'] == details['amount']
    assert 'test' in cleaned
    assert cleaned['test'] == 1

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_ALL)
def test_validate_request_fields_invalid_field_name():
    details = {'invalid': 'field'}

    try:
        conversions.validate_request_fields(details)
    except KeyError:
        assert True
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_API_FIELDS_INVALID)
def test_validate_request_fields_invalid_field_type():
    """Tests that error is generated if invalid field type is passed."""
    details = {'invalid': 'field'}

    try:
        conversions.validate_request_fields(details)
    except UnboundLocalError as error:
        assert str(error) == (
            "local variable 'cleaned_value' referenced before assignment"
        )
    else:
        assert False

def test_field_invalid_type():
    try:
        conversions.Field('invalid', 'x')
    except ValueError as error:
        assert str(error) == "Invalid field type provided for invalid: x"
    else:
        assert False

def test_process_request_fields_valid():
    api = {
        'account_id': '1',
        'token': '2',
        'terminal_id': '3',
    }
    cleaned = {
        'cc_cvv': '100.00',
    }
    additional = {
        'transactionType': 'purchase',
    }

    data = conversions.process_request_fields(api, cleaned, additional)

    assert 'accountId' in data
    assert 'apiToken' in data
    assert 'terminalId' in data
    assert 'cardCVV' in data
    assert 'transactionType' in data
    assert len(data) == 5

def test_process_request_fields_valid_no_additional():
    api = {
        'account_id': '1',
        'token': '2',
        'terminal_id': '3',
    }
    cleaned = {
        'cc_cvv': '100.00',
    }

    data = conversions.process_request_fields(api, cleaned)

    assert 'accountId' in data
    assert 'apiToken' in data
    assert 'terminalId' in data
    assert 'cardCVV' in data
    assert len(data) == 4

def test_process_request_fields_invalid_api():
    api = {
        'account_id': '1',
        'terminal_id': '3',
    }
    cleaned = {
        'cc_cvv': '100.00',
    }
    additional = {
        'transactionType': 'purchase',
    }

    try:
        conversions.process_request_fields(api, cleaned, additional)
    except KeyError as error:
        assert str(error) == "'token'"
    else:
        assert False

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_ALL)
def test_process_api_response_valid():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': 'API v2 being depreciated.',
        'transaction': {
            'amount': '50.01',
            'cardNumber': '1111********9999',
        }
    }
    raw_request = {
        'field_1': 'Field value 1',
        'field_2': 'Field value 2',
    }
    raw_response = 'This is a raw response.'

    response = conversions.process_api_response(
        api_response, raw_request, raw_response
    )

    assert len(response) == 8
    assert response['transaction_success'] is True
    assert response['response_message'] == 'Transaction successful.'
    assert response['notice'] == 'API v2 being depreciated.'
    assert 'field_1=Field value 1' in response['raw_request']
    assert 'field_2=Field value 2' in response['raw_request']
    assert response['raw_response'] == 'This is a raw response.'
    assert response['amount'] == Decimal('50.01')
    assert response['cc_number'] == '1111********9999'
    assert response['token_f4l4'] == '11119999'

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_STRING)
def test_process_api_response_string_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'cardNumber': '1111********9999',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['cc_number'] == '1111********9999'
    assert isinstance(response['cc_number'], str)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_DECIMAL)
def test_process_api_response_decimal_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'amount': '50.01',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['amount'] == Decimal('50.01')
    assert isinstance(response['amount'], Decimal)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_INTEGER)
def test_process_api_response_integer_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'transactionId': '101',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['transaction_id'] == 101
    assert isinstance(response['transaction_id'], int)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_BOOLEAN)
def test_process_api_response_boolean_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'availability': '1',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['availability'] is True
    assert isinstance(response['availability'], bool)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_DATE)
def test_process_api_response_date_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'date': '2018-01-01',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['transaction_date'] == date(2018, 1, 1)
    assert isinstance(response['transaction_date'], date)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_TIME)
def test_process_api_response_time_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'time': '08:30:15',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['transaction_time'] == time(8, 30, 15)
    assert isinstance(response['transaction_time'], time)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_ALL)
def test_process_api_response_missing_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
        'transaction': {
            'fake_field': 'fake.',
        }
    }

    response = conversions.process_api_response(api_response)

    assert response['fake_field'] == 'fake.'
    assert isinstance(response['fake_field'], str)

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_ALL)
def test_process_api_response_missing_required_field():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
    }

    try:
        conversions.process_api_response(api_response)
    except KeyError as error:
        assert str(error) == "'notice'"
    else:
        assert False

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_ALL)
def test_process_api_response_create_f4l4():
    api_response = {
        'response': 1,
        'responseMessage': '',
        'notice': '',
        'transaction': {
            'cardNumber': '1111********9999',
        }
    }
    response = conversions.process_api_response(api_response)

    assert response['token_f4l4'] == '11119999'

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_ALL)
def test_process_api_response_create_f4l4_with_no_cc():
    api_response = {
        'response': 1,
        'responseMessage': '',
        'notice': '',
        'transaction': {},
    }
    response = conversions.process_api_response(api_response)

    assert response['token_f4l4'] is None

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_ALL)
def test_process_api_response_missing_transaction():
    api_response = {
        'response': 1,
        'responseMessage': 'Transaction successful.',
        'notice': '',
    }

    response = conversions.process_api_response(api_response)

    assert len(response) == 5
    assert 'notice' in response
    assert 'raw_request' in response
    assert 'raw_response' in response
    assert 'response_message' in response
    assert 'transaction_success' in response

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_API_FIELDS_INVALID)
def test_process_api_response_invalid_type():
    api_response = {
        'response': 1,
        'responseMessage': '',
        'notice': '',
        'transaction': {
            'invalid': 'field',
        }
    }
    response = conversions.process_api_response(api_response)

    assert 'invalid' in response
    assert response['invalid'] == 'field'


def test_create_raw_response_with_data():
    response_data = {
        'accountId': '123456789',
        'token': '987654321',
    }

    request_string = conversions.create_raw_request(response_data)

    assert isinstance(request_string, str)
    assert 'accountId=123456789' in request_string
    assert 'token=987654321' in request_string

def test_create_raw_response_without_data():
    response_data = None

    request_string = conversions.create_raw_request(response_data)

    assert request_string is None
