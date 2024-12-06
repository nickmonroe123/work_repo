import pytest
from unittest.mock import Mock, patch
import json
from AccountProcess import AccountProcess
from structs import GeneralRequest, InternalRecord

@pytest.fixture
def account_process():
    """Create a basic AccountProcess instance for testing."""
    process = AccountProcess()
    # Set up basic ext_request data that many functions need
    process.ext_request = GeneralRequest()
    process.ext_request.phone_number = "1234567890"
    process.ext_request.first_name = "John"
    process.ext_request.last_name = "Doe"
    process.ext_request.zipcode5 = "12345"
    process.ext_request.email_address = "test@example.com"
    process.ext_request.street_number = "123"
    process.ext_request.street_name = "Main St"
    process.ext_request.city = "Anytown"
    process.ext_request.state = "CA"
    return process

@pytest.fixture
def mock_response():
    """Create a mock response for API calls."""
    mock = Mock()
    mock.json.return_value = {
        "getSpcAccountDivisionResponse": {
            "spcAccountDivisionList": [
                {
                    "accountNumber": "ACC123",
                    "uCAN": "UCAN123",
                    "emailAddress": "test@example.com"
                }
            ]
        }
    }
    mock.raise_for_status = Mock()
    return mock

def test_parse_spectrum_core_account_api_success(account_process, mock_response):
    """Test successful parsing of spectrum core account API response."""
    with patch('requests.request', return_value=mock_response):
        payload = {
            "getSpcAccountDivisionRequest": {
                "systemID": account_process.system_id,
                "telephoneNumber": "1234567890"
            }
        }
        result = account_process._parse_spectrum_core_account_api(
            payload, 
            function_name='test_function'
        )
        
        assert len(result) == 1
        assert result[0]['accountNumber'] == 'ACC123'
        assert len(account_process.core_services_list) == 1

def test_parse_spectrum_core_account_api_empty_response(account_process):
    """Test handling of empty response from spectrum core account API."""
    mock_empty = Mock()
    mock_empty.json.return_value = {
        "getSpcAccountDivisionResponse": {
            "spcAccountDivisionList": []
        }
    }
    mock_empty.raise_for_status = Mock()

    with patch('requests.request', return_value=mock_empty):
        payload = {
            "getSpcAccountDivisionRequest": {
                "systemID": account_process.system_id,
                "telephoneNumber": "1234567890"
            }
        }
        result = account_process._parse_spectrum_core_account_api(
            payload, 
            function_name='test_function'
        )
        
        assert len(result) == 0
        assert len(account_process.core_services_list) == 0

def test_phone_search_valid(account_process, mock_response):
    """Test phone search with valid phone number."""
    with patch('requests.request', return_value=mock_response):
        account_process.phone_search()
        assert len(account_process.core_services_list) == 1

def test_phone_search_invalid_number(account_process):
    """Test phone search with invalid phone number."""
    account_process.ext_request.phone_number = "123"  # Invalid length
    account_process.phone_search()
    assert len(account_process.core_services_list) == 0

def test_name_zip_search_valid(account_process, mock_response):
    """Test name and zip search with valid data."""
    with patch('requests.request', return_value=mock_response):
        account_process.name_zip_search()
        assert len(account_process.core_services_list) == 1

def test_name_zip_search_invalid_data(account_process):
    """Test name and zip search with invalid data."""
    account_process.ext_request.zipcode5 = "1234"  # Invalid length
    account_process.name_zip_search()
    assert len(account_process.core_services_list) == 0

def test_email_search_valid(account_process, mock_response):
    """Test email search with valid email."""
    with patch('requests.request', return_value=mock_response):
        account_process.email_search()
        assert len(account_process.core_services_list) == 1

def test_email_search_empty_email(account_process):
    """Test email search with empty email."""
    account_process.ext_request.email_address = ""
    account_process.email_search()
    assert len(account_process.core_services_list) == 0

def test_clean_address_search_matching_apartment(account_process):
    """Test clean address search with matching apartment numbers."""
    json_list = [{
        'addressLine2': 'Apt 123',
        'addressLine1': '123 Main St'
    }]
    account_process.ext_request.apartment = 'Apt 123'
    result = account_process.clean_address_search(json_list)
    assert len(result) == 1

def test_clean_address_search_no_match(account_process):
    """Test clean address search with non-matching apartment numbers."""
    json_list = [{
        'addressLine2': 'Apt 456',
        'addressLine1': '123 Main St'
    }]
    account_process.ext_request.apartment = 'Apt 123'
    result = account_process.clean_address_search(json_list)
    assert len(result) == 0

def test_address_search_valid(account_process, mock_response):
    """Test address search with valid address data."""
    with patch('requests.request', return_value=mock_response):
        account_process.address_search()
        assert len(account_process.core_services_list) == 1

def test_address_search_invalid_data(account_process):
    """Test address search with invalid address data."""
    account_process.ext_request.street_number = ""
    account_process.address_search()
    assert len(account_process.core_services_list) == 0

@pytest.fixture
def mock_billing_response():
    """Create a mock response for billing API calls."""
    mock = Mock()
    mock.json.return_value = {
        "findAccountResponse": {
            "accountList": [
                {
                    "accountNumber": "ACC123",
                    "firstName": "John",
                    "lastName": "Doe"
                }
            ]
        }
    }
    mock.raise_for_status = Mock()
    return mock

def test_billing_search_valid(account_process, mock_billing_response):
    """Test billing search with valid data."""
    with patch('requests.request', return_value=mock_billing_response):
        account_process.billing_search()
        assert len(account_process.core_services_list) == 1

def test_billing_search_invalid_data(account_process):
    """Test billing search with invalid data."""
    account_process.ext_request.last_name = ""
    account_process.billing_search()
    assert len(account_process.core_services_list) == 0

def test_billing_info_specific(account_process, mock_response):
    """Test billing info specific search."""
    dataset = [{"accountNumber": "ACC123"}]
    with patch('requests.request', return_value=mock_response):
        result = account_process.billing_info_specific(dataset)
        assert len(result) == 1
        assert result[0].get('uCAN') == 'UCAN123'
        assert result[0].get('emailAddress') == 'test@example.com'

def test_oracle_des_process_success(account_process):
    """Test oracle DES process with successful queries."""
    with patch('models.search_with_phone', return_value=[{'ACCT_NUM': 'ACC123'}]), \
         patch('models.search_with_address', return_value=[{'ACCT_NUM': 'ACC456'}]), \
         patch('models.search_with_email', return_value=[{'ACCT_NUM': 'ACC789'}]), \
         patch('models.search_with_zip_name', return_value=[{'ACCT_NUM': 'ACC101'}]):
        
        account_process.oracle_des_process()
        assert len(account_process.oracle_des_list) == 4

def test_oracle_des_process_failed_queries(account_process):
    """Test oracle DES process with failed queries."""
    with patch('models.search_with_phone', side_effect=Exception("DB Error")), \
         patch('models.search_with_address', side_effect=Exception("DB Error")), \
         patch('models.search_with_email', side_effect=Exception("DB Error")), \
         patch('models.search_with_zip_name', side_effect=Exception("DB Error")):
        
        account_process.oracle_des_process()
        assert len(account_process.oracle_des_list) == 0
