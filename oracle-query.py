import pytest
import json
import re
from unittest.mock import Mock, patch
import logging

from your_module import (
    AccountProcess, 
    FullIdentifier, 
    Name, 
    PhoneNumber, 
    Address,
    InternalRecord,
    IdentifiedAccount
)

# Utility function to create a test FullIdentifier
def create_test_full_identifier(
    first_name="John", 
    last_name="Doe", 
    phone_number="5551234567", 
    street_line1="123 Main St", 
    city="Anytown", 
    state="NY", 
    postal_code="12345",
    email="john.doe@example.com"
):
    return FullIdentifier(
        name=Name(first_name=first_name, last_name=last_name),
        phone_number=PhoneNumber(
            area_code=phone_number[:3], 
            exchange=phone_number[3:6], 
            line_number=phone_number[6:]
        ),
        address=Address(
            line1=street_line1, 
            city=city, 
            state=state, 
            postal_code=postal_code
        ),
        email=email
    )

# Phone Parsing Tests
def test_phone_parse():
    account_process = AccountProcess()

    # Test standard phone number
    phone = PhoneNumber(
        country_code="1", 
        area_code="555", 
        exchange="123", 
        line_number="4567"
    )
    assert account_process.phone_parse(phone) == "5551234567"

    # Test phone number with formatting
    phone_formatted = PhoneNumber(
        country_code="1", 
        area_code="(555)", 
        exchange="123", 
        line_number="4567"
    )
    assert account_process.phone_parse(phone_formatted) == "5551234567"

    # Test incomplete phone number
    phone_incomplete = PhoneNumber(
        area_code="555", 
        line_number="4567"
    )
    assert account_process.phone_parse(phone_incomplete) == "5554567"

    # Test empty phone number
    phone_empty = PhoneNumber()
    assert account_process.phone_parse(phone_empty) == ""

# Zip and Name Parsing Tests
def test_zip_name_parse():
    account_process = AccountProcess()

    # Standard case
    full_id = create_test_full_identifier(
        first_name="John", 
        last_name="Doe", 
        postal_code="12345"
    )
    first_name, last_name, zipcode = account_process.zip_name_parse(full_id)
    assert first_name == "John"
    assert last_name == "Doe"
    assert zipcode == "12345"

    # Postal code with extended zip
    full_id_extended = create_test_full_identifier(
        first_name="Jane", 
        last_name="Smith", 
        postal_code="12345-6789"
    )
    first_name, last_name, zipcode = account_process.zip_name_parse(full_id_extended)
    assert first_name == "Jane"
    assert last_name == "Smith"
    assert zipcode == "12345"

    # Empty name and postal code
    full_id_empty = FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    )
    first_name, last_name, zipcode = account_process.zip_name_parse(full_id_empty)
    assert first_name == ""
    assert last_name == ""
    assert zipcode == ""

# Address Parsing Tests
def test_address_parse():
    account_process = AccountProcess()

    # Standard address
    address = Address(line1="123 Main St", city="Anytown", state="NY", line2="Apt 4B")
    street_number, street_name, city, state, apartment = account_process.address_parse(address)
    assert street_number == "123"
    assert street_name == "Main St"
    assert city == "Anytown"
    assert state == "NY"
    assert apartment == "Apt 4B"

    # Address without apartment
    address_no_apt = Address(line1="456 Oak Rd", city="Smallville", state="CA")
    street_number, street_name, city, state, apartment = account_process.address_parse(address_no_apt)
    assert street_number == "456"
    assert street_name == "Oak Rd"
    assert city == "Smallville"
    assert state == "CA"
    assert apartment == ""

    # Edge case: Street name without number
    address_no_number = Address(line1="Broadway", city="New York", state="NY")
    street_number, street_name, city, state, apartment = account_process.address_parse(address_no_number)
    assert street_number == ""
    assert street_name == "Broadway"
    assert city == "New York"
    assert state == "NY"
    assert apartment == ""

# Request Initialization Tests
def test_ext_request_init():
    account_process = AccountProcess()

    # Full identifier with complete information
    full_id = create_test_full_identifier()
    account_process.ext_request_init(full_id)

    assert account_process.ext_request.phone_number == "5551234567"
    assert account_process.ext_request.first_name == "John"
    assert account_process.ext_request.last_name == "Doe"
    assert account_process.ext_request.zipcode5 == "12345"
    assert account_process.ext_request.email_address == "john.doe@example.com"
    assert account_process.ext_request.street_number == "123"
    assert account_process.ext_request.street_name == "Main St"
    assert account_process.ext_request.city == "Anytown"
    assert account_process.ext_request.state == "NY"

    # Minimal identifier
    minimal_id = FullIdentifier(
        name=Name(first_name="Minimal", last_name="User"),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    )
    account_process.ext_request_init(minimal_id)
    assert account_process.ext_request.first_name == "Minimal"
    assert account_process.ext_request.last_name == "User"

# Full Search Process Mock Tests
@patch('your_module.AccountProcess.phone_search')
@patch('your_module.AccountProcess.name_zip_search')
@patch('your_module.AccountProcess.email_search')
@patch('your_module.AccountProcess.address_search')
@patch('your_module.AccountProcess.billing_search')
@patch('your_module.AccountProcess.confirmed_matches')
@patch('your_module.AccountProcess.oracle_des_process')
def test_full_search_process(
    mock_oracle_des_process,
    mock_confirmed_matches,
    mock_billing_search,
    mock_address_search,
    mock_email_search,
    mock_name_zip_search,
    mock_phone_search
):
    account_process = AccountProcess()

    # Setup mock returns
    mock_phone_search.return_value = None
    mock_name_zip_search.return_value = None
    mock_email_search.return_value = None
    mock_address_search.return_value = None
    mock_billing_search.return_value = None
    mock_confirmed_matches.return_value = []
    mock_oracle_des_process.return_value = None

    # Create a full identifier
    full_id = create_test_full_identifier()

    # Run full search
    result = account_process.full_search(full_id)

    # Verify method calls
    mock_phone_search.assert_called_once()
    mock_name_zip_search.assert_called_once()
    mock_email_search.assert_called_once()
    mock_address_search.assert_called_once()
    mock_billing_search.assert_called_once()
    mock_oracle_des_process.assert_called_once()

# Error Handling Tests
def test_full_search_error_handling():
    account_process = AccountProcess()

    # Create an invalid full identifier
    invalid_id = FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    )

    # Capture logging output
    with pytest.raises(Exception):
        with patch('logging.info') as mock_logger:
            account_process.full_search(invalid_id)
            # Verify logging calls
            assert mock_logger.call_count > 0

# Configuration and Constant Tests
def test_account_process_configuration():
    # Test core service URLs
    assert AccountProcess.SPECTRUM_CORE_API == "https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept"
    assert AccountProcess.SPECTRUM_CORE_ACCOUNT.startswith(AccountProcess.SPECTRUM_CORE_API)
    assert AccountProcess.SPECTRUM_CORE_BILLING.startswith(AccountProcess.SPECTRUM_CORE_API)
    
    # Test system ID
    assert AccountProcess.SPECTRUM_CORE_SYSTEM_ID == "ComplianceService"

# Extensive Parametrized Tests
@pytest.mark.parametrize("test_input", [
    # Standard full name
    create_test_full_identifier(first_name="John", last_name="Doe"),
    
    # Unicode names
    create_test_full_identifier(first_name="José", last_name="García"),
    
    # Very long names
    create_test_full_identifier(first_name="A" * 50, last_name="B" * 50),
    
    # Minimal information
    FullIdentifier(
        name=Name(first_name="Mini", last_name="User"),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email=""
    ),
    
    # International address
    create_test_full_identifier(
        street_line1="789 International St", 
        city="Toronto", 
        state="ON", 
        postal_code="M5V 2T6"
    )
])
def test_comprehensive_full_identifier_processing(test_input):
    account_process = AccountProcess()
    
    try:
        # Run full search
        results = account_process.full_search(test_input)
        
        # Basic validation
        assert isinstance(results, list)
        
        # Optional: More specific checks based on type of input
        if results:
            for result in results:
                assert isinstance(result, IdentifiedAccount)
    
    except Exception as e:
        # Unexpected errors should fail the test
        pytest.fail(f"Unexpected error in processing: {e}")

# Performance and Stress Tests
def test_performance_full_search(benchmark):
    account_process = AccountProcess()
    full_id = create_test_full_identifier()
    
    def run_full_search():
        return account_process.full_search(full_id)
    
    # Benchmark the full search process
    result = benchmark(run_full_search)
    
    assert result is not None
    assert isinstance(result, list)
