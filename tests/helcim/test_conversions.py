"""Tests for the conversions module."""
# pylint: disable=protected-access

from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

from helcim import conversions

# *_API_FIELDS being mocked to allow proper testing of validation
MOCK_TO_FIELDS_DECIMAL = {
    'amount': conversions.Field('amount', 'c', 10, 100),
}

MOCK_TO_FIELDS_STRING = {
    'cc_cvv': conversions.Field('cardCVV', 's', 3, 4),
}

MOCK_TO_FIELDS_INTEGER = {
    'product_id': conversions.Field('productId', 'i', 1, 100),
}

MOCK_TO_FIELDS_BOOLEAN = {
    'test': conversions.Field('test', 'b'),
}

MOCK_TO_FIELDS_ALL = {
    'amount': conversions.Field('amount', 'c', 10, 100),
    'cc_cvv': conversions.Field('cardCVV', 's', 3, 4),
    'product_id': conversions.Field('productId', 'i', 1, 100),
    'test': conversions.Field('test', 'b'),
}

MOCK_TO_FIELDS_INVALID = {
    'invalid': conversions.Field('value', 't'),
}

MOCK_FROM_FIELDS = {
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

MOCK_FROM_FIELDS_INVALID = {
    'invalid': InvalidField('field', 'x')
}

def test__field__invalid_type():
    """Confirms object handling of an invalid field type."""
    try:
        conversions.Field('invalid', 'x')
    except ValueError as error:
        assert str(error) == "Invalid field type provided for invalid: x"
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_STRING)
def test__validate_request_fields__string_valid():
    """Confirms handling of string request field."""
    details = {
        'cc_cvv': '123'
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'cc_cvv' in cleaned
    assert cleaned['cc_cvv'] == details['cc_cvv']

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_STRING)
def test__validate_request_fields__string_min_invalid():
    """Confirms handling of string minimum length validation."""
    details = {
        'cc_cvv': '12'
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "cc_cvv field length too short."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_STRING)
def test__validate_request_fields__string_max_invalid():
    """Confirms handling of string maximum length validation."""
    details = {
        'cc_cvv': '12345'
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "cc_cvv field length too long."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_INTEGER)
def test__validate_request_fields__integer_valid():
    """Confirms handling of integer request field."""
    details = {
        'product_id': 100
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'product_id' in cleaned
    assert cleaned['product_id'] == details['product_id']

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_INTEGER)
def test__validate_request_fields__integer_min():
    """Confirms handling of integer minimum value validation."""
    details = {
        'product_id': 0
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "product_id field value too small."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_INTEGER)
def test__validate_request_fields__integer_max():
    """Confirms handling of integer maximum value validation."""
    details = {
        'product_id': 101
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "product_id field value too large."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_DECIMAL)
def test__validate_request_fields__decimal_valid():
    """Confirms handling of decimal request field."""
    details = {
        'amount': Decimal('50.00')
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'amount' in cleaned
    assert cleaned['amount'] == details['amount']

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_DECIMAL)
def test__validate_request_fields__decimal_min():
    """Confirms handling of decimal minimum value validation."""
    details = {
        'amount': Decimal('1.00')
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "amount field value too small."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_DECIMAL)
def test__validate_request_fields__decimal_max():
    """Confirms handling of decimal minimum value validation."""
    details = {
        'amount': Decimal('200.00')
    }

    try:
        conversions.validate_request_fields(details)
    except ValueError as error:
        assert str(error) == "amount field value too large."
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_BOOLEAN)
def test__validate_request_fields__boolean_true():
    """Confirms handling of True boolean request field."""
    details = {
        'test': True
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'test' in cleaned
    assert cleaned['test'] == 1

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_BOOLEAN)
def test__validate_request_fields__boolean_false():
    """Confirms handling of False boolean request field."""
    details = {
        'test': False
    }

    cleaned = conversions.validate_request_fields(details)

    assert 'test' in cleaned
    assert cleaned['test'] == 0

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_ALL)
def test__validate_request_fields__all_valid():
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

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_ALL)
def test__validate_request_fields__invalid_field_name():
    """Confirms handling when an invalid field name provide."""
    details = {'invalid': 'field'}

    try:
        conversions.validate_request_fields(details)
    except KeyError:
        assert True
    else:
        assert False

@patch('helcim.conversions.TO_API_FIELDS', MOCK_TO_FIELDS_INVALID)
def test__validate_request_fields__invalid_field_type():
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

def test__process_request_fields__valid():
    """Confirms handling of Python data to Helcim API data."""
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

def test__process_request_fields__valid_no_additional():
    """Confirms handling of Python data conversion with no extra details."""
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

def test__process_request_fields__invalid_api():
    """Confirms handling when API details is invalid."""
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

def test__process_api_response__string_field():
    """Confirms handling of an API string response field."""
    fields = {'cardNumber': '1111********9999'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['cc_number'] == '1111********9999'
    assert isinstance(response['cc_number'], str)

def test__convert_helcim_response_string__field_none():
    """Tests that string field can handle a None response."""
    fields = {'cardNumber': None}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['cc_number'] is None

def test_process_api_response__decimal_field():
    """Confirms handling of an API decimal response field."""
    fields = {'amount': '50.01'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['amount'] == Decimal('50.01')
    assert isinstance(response['amount'], Decimal)

def test__convert_helcim_response__integer_field():
    """Confirms handling of an API integer response field."""
    fields = {'transactionId': '101'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['transaction_id'] == 101
    assert isinstance(response['transaction_id'], int)

def test__convert_helcim_response__boolean_field():
    """Confirms handling of an API boolean response field."""
    fields = {'availability': '1'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['availability'] is True
    assert isinstance(response['availability'], bool)

def test__convert_helcim_response__date_field():
    """Confirms handling of an API date response field."""
    fields = {'date': '2018-01-01'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['transaction_date'] == date(2018, 1, 1)
    assert isinstance(response['transaction_date'], date)

def test__convert_helcim_response__time_field():
    """Confirms handling of an API time response field."""
    fields = {'time': '08:30:15'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['transaction_time'] == time(8, 30, 15)
    assert isinstance(response['transaction_time'], time)

def test_process_api_response_missing_field():
    """Confirms handling of an API response field not accounted for."""
    fields = {'fake_field': 'fake.'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS
    )

    assert response['fake_field'] == 'fake.'
    assert isinstance(response['fake_field'], str)

def test__convert_helcim_response__invalid_type():
    """Confirms handling of an invalid type for a response field."""
    fields = {'invalid': 'field'}

    response = conversions.convert_helcim_response_fields(
        fields, MOCK_FROM_FIELDS_INVALID
    )

    assert 'invalid' in response
    assert response['invalid'] == 'field'

def test__create_f4l4():
    """Confirms the F4L4 is returned when cc_number provided."""
    token_f4l4 = conversions.create_f4l4('1111********9999')

    assert token_f4l4 == '11119999'

def test__create_f4l4__with_whitespace():
    """Confirms the F4L4 is returned when cc_number provided."""
    token_f4l4 = conversions.create_f4l4(' 1111********9999 ')

    assert token_f4l4 == '11119999'

def test__create_f4l4__no_cc():
    """Confirms the F4L4 creation can handle a missing CC number."""
    token_f4l4 = conversions.create_f4l4(None)

    assert token_f4l4 is None

def test__create_raw_response__with_data():
    """Confirms handling when data is provided."""
    response_data = {
        'accountId': '123456789',
        'token': '987654321',
    }

    request_string = conversions.create_raw_request(response_data)

    assert isinstance(request_string, str)
    assert 'accountId=123456789' in request_string
    assert 'token=987654321' in request_string

def test__create_raw_response__without_data():
    """Confirms handling when data is not provided."""
    response_data = None

    request_string = conversions.create_raw_request(response_data)

    assert request_string is None

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_FIELDS)
def test__process_api_response__valid():
    """Tests handling of a valid API response."""
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

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_FIELDS)
def test__process_api_response__missing_transaction():
    """Confirms handling of an API response when transaction field missing."""
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

def test__process_api_response__missing_required_field():
    """Confirms handling when a required field is missing."""
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

@patch('helcim.conversions.FROM_API_FIELDS', MOCK_FROM_FIELDS)
def test__process_helcim_js__expected_output():
    """Confirms output from function."""
    api_response = {
        'amount': '100.00',
        'cardNumber': '1111********9999',
    }

    response = conversions.process_helcim_js_response(api_response)

    # Length of response should be 3 (cardNumber will trigger F4L4 creation)
    assert len(response) == 3
    assert 'amount' in response
    assert 'cc_number' in response
    assert 'token_f4l4' in response
