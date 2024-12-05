import pytest
import msgspec

from your_module import (
    IdentifiedAccount,
    GeneralRequest,
    Description,
    InternalRecord,
    OracleDESRecord,
    Name,
    PhoneNumber,
    Address,
    FullIdentifier
)

# Name Struct Tests
def test_name_struct():
    # Basic full name
    name1 = Name(first_name="John", last_name="Doe")
    assert name1.first_name == "John"
    assert name1.last_name == "Doe"
    assert name1.middle_name == ""
    assert name1.suffix == ""
    assert name1.prefix == ""

    # Full name with all optional fields
    name2 = Name(
        first_name="John", 
        last_name="Smith", 
        middle_name="Michael", 
        suffix="Jr.", 
        prefix="Dr."
    )
    assert name2.first_name == "John"
    assert name2.last_name == "Smith"
    assert name2.middle_name == "Michael"
    assert name2.suffix == "Jr."
    assert name2.prefix == "Dr."

    # Edge cases
    with pytest.raises(TypeError):
        Name()  # Missing required fields

    # Unicode names
    name3 = Name(first_name="José", last_name="González")
    assert name3.first_name == "José"
    assert name3.last_name == "González"

# PhoneNumber Struct Tests
def test_phone_number_struct():
    # Complete phone number
    phone1 = PhoneNumber(
        country_code="1", 
        area_code="123", 
        exchange="456", 
        line_number="7890",
        extension="123",
        type_code="mobile"
    )
    assert phone1.country_code == "1"
    assert phone1.area_code == "123"
    assert phone1.exchange == "456"
    assert phone1.line_number == "7890"
    assert phone1.extension == "123"
    assert phone1.type_code == "mobile"

    # Minimal phone number
    phone2 = PhoneNumber(line_number="5551234")
    assert phone2.line_number == "5551234"
    assert phone2.country_code == ""
    assert phone2.area_code == ""

    # International phone numbers
    phone3 = PhoneNumber(
        country_code="44", 
        area_code="20", 
        line_number="12345678"
    )
    assert phone3.country_code == "44"
    assert phone3.area_code == "20"
    assert phone3.line_number == "12345678"

# Address Struct Tests
def test_address_struct():
    # Complete address
    address1 = Address(
        city="New York", 
        state="NY", 
        line1="123 Main St", 
        postal_code="10001",
        line2="Apt 4B",
        country_code="US"
    )
    assert address1.city == "New York"
    assert address1.state == "NY"
    assert address1.line1 == "123 Main St"
    assert address1.postal_code == "10001"
    assert address1.line2 == "Apt 4B"
    assert address1.country_code == "US"

    # Minimal address
    address2 = Address(
        city="Chicago", 
        state="IL", 
        line1="456 Oak Rd", 
        postal_code="60601"
    )
    assert address2.line2 == ""
    assert address2.country_code == ""

    # International addressing
    address3 = Address(
        city="Toronto", 
        state="ON", 
        line1="789 Maple Ave", 
        postal_code="M5V 2T6",
        country_code="CA"
    )
    assert address3.country_code == "CA"

    # Edge case: missing required fields
    with pytest.raises(TypeError):
        Address(line1="Test Street")

# FullIdentifier Struct Tests
def test_full_identifier_struct():
    # Complete full identifier
    full_id = FullIdentifier(
        name=Name(first_name="Alice", last_name="Johnson"),
        phone_number=PhoneNumber(line_number="5551234"),
        address=Address(
            city="San Francisco", 
            state="CA", 
            line1="789 Tech Lane", 
            postal_code="94105"
        ),
        email="alice.johnson@example.com"
    )
    assert full_id.name.first_name == "Alice"
    assert full_id.phone_number.line_number == "5551234"
    assert full_id.address.city == "San Francisco"
    assert full_id.email == "alice.johnson@example.com"

    # Edge cases: minimal information
    with pytest.raises(TypeError):
        FullIdentifier()  # Missing all required fields

# GeneralRequest Struct Tests
def test_general_request_struct():
    # Full information request
    request1 = GeneralRequest(
        country_code="1",
        phone_number="5551234567",
        first_name="Bob",
        last_name="Smith",
        zipcode5="12345",
        email_address="bob.smith@example.com",
        street_number="100",
        street_name="Main St",
        city="Anytown",
        state="NY",
        apartment="4B"
    )
    assert request1.first_name == "Bob"
    assert request1.zipcode5 == "12345"
    assert request1.apartment == "4B"

    # Minimal information request
    request2 = GeneralRequest(first_name="Jane")
    assert request2.first_name == "Jane"
    assert request2.phone_number == ""
    assert request2.zipcode5 == ""

# InternalRecord Struct Tests
def test_internal_record_struct():
    # Full internal record
    record1 = InternalRecord(
        ucan="12345",
        division_id="DIV001",
        account_status="Active",
        first_name="John",
        last_name="Doe",
        _address_line_1="100 Main St",
        _address_line_2="Apt 4B",
        city="Anytown",
        state="NY"
    )
    assert record1.ucan == "12345"
    assert record1.street_number == "100"
    assert record1.full_address == "100 Main St Apt 4B Anytown NY"
    assert record1.full_address_no_apt == "100 Main St Anytown NY"

    # Address parsing edge cases
    record2 = InternalRecord(_address_line_1="")
    assert record2.street_number == ""
    assert record2.street_name == ""

# OracleDESRecord Struct Tests
def test_oracle_des_record_struct():
    # Full Oracle DES record
    record1 = OracleDESRecord(
        ACCT_NUM="98765",
        PRIMARY_NUMBER="5551234567",
        ACCT_NAME="Doe,John",
        PSTL_CD_TXT_BLR="12345",
        CITY_NM_BLR="Anytown",
        STATE_NM_BLR="NY",
        BLR_ADDR1_LINE="100 Main St",
        BLR_ADDR2_LINE="Apt 4B"
    )
    assert record1.account_number == "98765"
    assert record1.first_name == "John"
    assert record1.last_name == "Doe"
    assert record1.full_address == "100 Main St Apt 4B Anytown NY"

    # Name parsing edge cases
    record2 = OracleDESRecord(ACCT_NAME="SingleName")
    assert record2.first_name == ""
    assert record2.last_name == ""

# IdentifiedAccount Struct Tests
def test_identified_account_struct():
    # Full identified account
    account1 = IdentifiedAccount(
        name=Name(first_name="Alice", last_name="Johnson"),
        phone_number=PhoneNumber(line_number="5551234"),
        address=Address(
            city="San Francisco", 
            state="CA", 
            line1="789 Tech Lane", 
            postal_code="94105"
        ),
        email="alice.johnson@example.com",
        match_score=0.95,
        account_type="Premium",
        status="Active",
        source="Internal",
        ucan="12345"
    )
    assert account1.match_score == 0.95
    assert account1.account_type == "Premium"
    assert account1.ucan == "12345"

    # Minimal identified account
    account2 = IdentifiedAccount(
        name=Name(first_name="Bob", last_name="Smith"),
        phone_number=PhoneNumber(),
        address=Address(
            city="Anytown", 
            state="NY", 
            line1="100 Main St", 
            postal_code="12345"
        ),
        email=""
    )
    assert account2.match_score == 0.0
    assert account2.account_type == ""

# Performance and Serialization Tests
def test_struct_serialization():
    # Test msgspec serialization and deserialization
    name = Name(first_name="John", last_name="Doe")
    encoded = msgspec.json.encode(name)
    decoded = msgspec.json.decode(encoded, type=Name)
    assert decoded == name

# Boundary and Stress Tests
def test_extreme_input_lengths():
    # Very long inputs
    long_name = Name(
        first_name="A" * 100, 
        last_name="B" * 100, 
        middle_name="C" * 50, 
        suffix="D" * 10
    )
    assert len(long_name.first_name) == 100
    assert len(long_name.last_name) == 100

    # Unicode stress test
    unicode_name = Name(
        first_name="アリス", 
        last_name="田中", 
        middle_name="まりこ"
    )
    assert unicode_name.first_name == "アリス"
    assert unicode_name.last_name == "田中"

# Validation Tests for Different Data Sources
def test_data_source_conversions():
    # Convert between different record types
    oracle_record = OracleDESRecord(
        ACCT_NUM="12345",
        ACCT_NAME="Doe,John",
        PRIMARY_NUMBER="5551234567"
    )
    
    general_request = GeneralRequest(
        account_number=oracle_record.account_number,
        first_name=oracle_record.first_name,
        last_name=oracle_record.last_name,
        phone_number=oracle_record.phone_number
    )
    
    assert general_request.account_number == "12345"
    assert general_request.first_name == "John"
    assert general_request.phone_number == "5551234567"

# Performance Comparison Test
def test_struct_performance(benchmark):
    # Benchmark struct creation
    def create_full_identifier():
        return FullIdentifier(
            name=Name(first_name="John", last_name="Doe"),
            phone_number=PhoneNumber(line_number="5551234"),
            address=Address(
                city="Anytown", 
                state="NY", 
                line1="100 Main St", 
                postal_code="12345"
            ),
            email="john.doe@example.com"
        )
    
    result = benchmark(create_full_identifier)
    assert result is not None
