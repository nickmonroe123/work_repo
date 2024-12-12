import json
from unittest.mock import Mock, patch

import msgspec
import pytest
from account_identification.structs import *
from identifiers.structs import *
from services import AccountProcess


# Utility function to create a test FullIdentifier
def create_test_full_identifier(
    first_name="John",
    last_name="Doe",
    phone_number="5551234567",
    street_line1="123 Main St",
    city="Anytown",
    state="NY",
    postal_code="12345",
    email="john.doe@example.com",
):
    return FullIdentifier(
        name=Name(first_name=first_name, last_name=last_name),
        phone_number=PhoneNumber(
            area_code=phone_number[:3],
            exchange=phone_number[3:6],
            line_number=phone_number[6:],
        ),
        address=Address(
            line1=street_line1, city=city, state=state, postal_code=postal_code
        ),
        email=email,
    )

# Phone Parsing Tests
def test_phone_parse():
    account_process = AccountProcess()

    # Test standard phone number
    phone = PhoneNumber(
        country_code="1", area_code="555", exchange="123", line_number="4567"
    )
    assert account_process.phone_parse(phone) == "5551234567"

    # Test phone number with formatting
    phone_formatted = PhoneNumber(
        country_code="1", area_code="(555)", exchange="123", line_number="4567"
    )
    assert account_process.phone_parse(phone_formatted) == "5551234567"

    # Test incomplete phone number
    phone_incomplete = PhoneNumber(area_code="555", line_number="4567")
    assert account_process.phone_parse(phone_incomplete) == "5554567"

    # Test empty phone number
    phone_empty = PhoneNumber()
    assert account_process.phone_parse(phone_empty) == ""


# Zip and Name Parsing Tests
def test_zip_name_parse():
    account_process = AccountProcess()

    # Standard case
    full_id = create_test_full_identifier(
        first_name="John", last_name="Doe", postal_code="12345"
    )
    first_name, last_name, zipcode = account_process.zip_name_parse(full_id)
    assert first_name == "John"
    assert last_name == "Doe"
    assert zipcode == "12345"

    # Postal code with extended zip
    full_id_extended = create_test_full_identifier(
        first_name="Jane", last_name="Smith", postal_code="12345-6789"
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
        email="",
    )
    first_name, last_name, zipcode = account_process.zip_name_parse(full_id_empty)
    assert first_name == ""
    assert last_name == ""
    assert zipcode == ""


# Address Parsing Tests
def test_address_parse():
    account_process = AccountProcess()

    # Standard address
    address = Address(
        line1="123 Main St",
        city="Anytown",
        state="NY",
        line2="Apt 4B",
        postal_code="62323",
    )
    street_number, street_name, city, state, apartment = account_process.address_parse(
        address
    )
    assert street_number == "123"
    assert street_name == "Main St"
    assert city == "Anytown"
    assert state == "NY"
    assert apartment == "Apt 4B"

    # Address without apartment
    address_no_apt = Address(
        line1="456 Oak Rd", city="Smallville", state="CA", postal_code="62323"
    )
    street_number, street_name, city, state, apartment = account_process.address_parse(
        address_no_apt
    )
    assert street_number == "456"
    assert street_name == "Oak Rd"
    assert city == "Smallville"
    assert state == "CA"
    assert apartment == ""

    # Edge case: missing zipcode somehow
    with pytest.raises(TypeError):
        Address(line1="123 Main St", city="Anytown", state="NY", line2="Apt 4B")

    # Edge case: missing city somehow
    with pytest.raises(TypeError):
        Address(line1="123 Main St", state="NY", line2="Apt 4B", postal_code="62323")

    # Edge case: missing address line 1 somehow
    with pytest.raises(TypeError):
        Address(city="Anytown", state="NY", line2="Apt 4B", postal_code="62323")

    # Edge case: missing state somehow
    with pytest.raises(TypeError):
        Address(
            line1="123 Main St", city="Anytown", line2="Apt 4B", postal_code="62323"
        )

    # Edge case: Street name without number
    address_no_number = Address(
        line1="Broadway", city="New York", state="NY", postal_code="62323"
    )
    street_number, street_name, city, state, apartment = account_process.address_parse(
        address_no_number
    )
    assert street_number == ""
    assert street_name == "Broadway"
    assert city == "New York"
    assert state == "NY"
    assert apartment == ""

    # Edge case: Street number without name
    address_no_number = Address(
        line1="756", city="New York", state="NY", postal_code="62323"
    )
    street_number, street_name, city, state, apartment = account_process.address_parse(
        address_no_number
    )
    assert street_number == "756"
    assert street_name == ""
    assert city == "New York"
    assert state == "NY"
    assert apartment == ""

    # Edge case: Street name without number but weird street name
    address_no_number = Address(
        line1="756th street", city="New York", state="NY", postal_code="62323"
    )
    street_number, street_name, city, state, apartment = account_process.address_parse(
        address_no_number
    )
    assert street_number == "756th"
    assert street_name == "street"
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
        email="",
    )
    account_process.ext_request_init(minimal_id)
    assert account_process.ext_request.first_name == "Minimal"
    assert account_process.ext_request.last_name == "User"


# Error Handling Tests
def test_full_search_error_handling():
    account_process = AccountProcess()

    # Create an invalid full identifier
    invalid_id = FullIdentifier(
        name=Name(first_name="", last_name=""),
        phone_number=PhoneNumber(),
        address=Address(city="", state="", line1="", postal_code=""),
        email="",
    )

    # Capture logging output
    with pytest.raises(Exception):
        with patch('logging.info') as mock_logger:
            account_process.full_search(invalid_id)
            # Verify logging calls
            assert mock_logger.call_count > 0


# Extensive Parametrized Tests
@pytest.mark.parametrize(
    "test_input",
    [
        # Standard full name
        create_test_full_identifier(first_name="John", last_name="Doe"),
        # Unicode names
        create_test_full_identifier(first_name="José", last_name="García"),
        # Very long names
        create_test_full_identifier(first_name="A" * 50, last_name="B" * 50),
        # Minimal information - just name
        FullIdentifier(
            name=Name(first_name="Mini", last_name="User"),
            phone_number=PhoneNumber(),
            address=Address(city="", state="", line1="", postal_code=""),
            email="",
        ),
        # Minimal information - just phone number
        FullIdentifier(
            name=Name(first_name="", last_name=""),
            phone_number=PhoneNumber(
                area_code="555", exchange="666", line_number="7777"
            ),
            address=Address(city="", state="", line1="", postal_code=""),
            email="",
        ),
        # Minimal information - just bad phone number
        FullIdentifier(
            name=Name(first_name="", last_name=""),
            phone_number=PhoneNumber(
                area_code="2555", exchange="6266", line_number="77727"
            ),
            address=Address(city="", state="", line1="", postal_code=""),
            email="",
        ),
        # Minimal information - just address
        FullIdentifier(
            name=Name(first_name="", last_name=""),
            phone_number=PhoneNumber(),
            address=Address(
                city="Alton", state="IL", line1="213 street", postal_code="62002"
            ),
            email="",
        ),
        # Minimal information - just email
        FullIdentifier(
            name=Name(first_name="", last_name=""),
            phone_number=PhoneNumber(),
            address=Address(city="", state="", line1="", postal_code=""),
            email="testemail@outlook.com",
        ),
        # Minimal information - full name, bad state
        FullIdentifier(
            name=Name(first_name="Luke", last_name="Test"),
            phone_number=PhoneNumber(),
            address=Address(city="", state="ASD", line1="", postal_code=""),
            email="testemail@outlook.com",
        ),
        # Minimal information - full name, bad zip
        FullIdentifier(
            name=Name(first_name="Luke", last_name="Test"),
            phone_number=PhoneNumber(),
            address=Address(city="", state="", line1="", postal_code="123"),
            email="testemail@outlook.com",
        ),
        # Full data, bad input
        FullIdentifier(
            name=Name(first_name="Luke", last_name="Test"),
            phone_number=PhoneNumber(
                area_code="2555", exchange="6266", line_number="77727"
            ),
            address=Address(city="", state="ALS", line1="", postal_code="123"),
            email="",
        ),
        # International address
        create_test_full_identifier(
            street_line1="789 International St",
            city="Toronto",
            state="ON",
            postal_code="M5V 2T6",
        ),
    ],
)
def test_comprehensive_full_identifier_processing(test_input):
    account_process = AccountProcess()

    try:
        # Run full search
        results = account_process.full_search(test_input)

        # Optional: More specific checks based on type of input
        if results:
            for result in results:
                assert results is None or isinstance(result, IdentifiedAccount)

    except Exception as e:
        # Unexpected errors should fail the test
        pytest.fail(f"Unexpected error in processing: {e}")


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
                    "emailAddress": "test@example.com",
                }
            ]
        }
    }
    mock.raise_for_status = Mock()
    return mock


def test_phone_search_invalid_number(account_process):
    """Test phone search with invalid phone number."""
    account_process.core_services_list = []
    account_process.ext_request.phone_number = "123"  # Invalid length
    account_process.phone_search()
    assert len(account_process.core_services_list) == 0


def test_name_zip_search_invalid_data(account_process):
    """Test name and zip search with invalid data."""
    account_process.core_services_list = []
    account_process.ext_request.zipcode5 = "1234"  # Invalid length
    account_process.name_zip_search()
    assert len(account_process.core_services_list) == 0


def test_email_search_empty_email(account_process):
    """Test email search with empty email."""
    account_process.core_services_list = []
    account_process.ext_request.email_address = ""
    account_process.email_search()
    assert len(account_process.core_services_list) == 0


def test_clean_address_search_matching_apartment(account_process):
    """Test clean address search with matching apartment numbers."""
    json_list = [{'addressLine2': 'Apt 123', 'addressLine1': '123 Main St'}]
    account_process.ext_request.apartment = 'Apt 123'
    result = account_process.clean_address_search(json_list)
    assert len(result) == 1


def test_clean_address_search_no_match(account_process):
    """Test clean address search with non-matching apartment numbers."""
    json_list = [{'addressLine2': 'Apt 456', 'addressLine1': '123 Main St'}]
    account_process.ext_request.apartment = 'Apt 123'
    result = account_process.clean_address_search(json_list)
    assert len(result) == 0


def test_address_search_invalid_data(account_process):
    account_process.core_services_list = []
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
                {"accountNumber": "ACC123", "firstName": "John", "lastName": "Doe"}
            ]
        }
    }
    mock.raise_for_status = Mock()
    return mock


def test_billing_search_invalid_data(account_process):
    account_process.core_services_list = []
    """Test billing search with invalid data."""
    account_process.ext_request.last_name = ""
    account_process.billing_search()
    assert len(account_process.core_services_list) == 0


def test_oracle_des_process_failed_queries(account_process):
    """Test oracle DES process with failed queries."""
    with (
        patch('models.search_with_phone', side_effect=Exception("DB Error")),
        patch('models.search_with_address', side_effect=Exception("DB Error")),
        patch('models.search_with_email', side_effect=Exception("DB Error")),
        patch('models.search_with_zip_name', side_effect=Exception("DB Error")),
    ):
        account_process.oracle_des_process()
        assert len(account_process.oracle_des_list) == 0
