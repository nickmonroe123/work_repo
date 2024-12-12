from unittest import TestCase, mock
from parameterized import parameterized
from datetime import datetime
from typing import Optional

# Import the classes to test
from .models import (
    IdentifiedAccount,
    InternalRecord,
    OracleDESRecord,
    GeneralRequest,
    Description
)

class TestInternalRecord(TestCase):
    
    # fmt: off
    @parameterized.expand([
        ('standard_address', 
         '123 Main Street', 
         '', 
         'New York', 
         'NY',
         '123 Main Street New York NY',
         '123',
         'Main Street'),
        
        ('address_with_apt', 
         '456 Oak Avenue', 
         'Apt 2B', 
         'Boston', 
         'MA',
         '456 Oak Avenue Apt 2B Boston MA',
         '456',
         'Oak Avenue'),
         
        ('empty_address',
         '',
         '',
         'Chicago',
         'IL',
         ' Chicago IL',
         '',
         ''),
         
        ('complex_address',
         '789-A Pine Boulevard',
         'Suite 100',
         'Miami',
         'FL',
         '789-A Pine Boulevard Suite 100 Miami FL',
         '789-A',
         'Pine Boulevard'),
    ])
    # fmt: on
    def test_internal_record_address_parsing(
        self, 
        name: str, 
        address_line1: str,
        address_line2: str,
        city: str,
        state: str,
        expected_full_address: str,
        expected_street_number: str,
        expected_street_name: str
    ):
        record = InternalRecord(
            addressLine1=address_line1,
            addressLine2=address_line2,
            city=city,
            state=state,
            accountType=Description(description="Residential")
        )
        
        self.assertEqual(record.full_address.strip(), expected_full_address.strip())
        self.assertEqual(record.street_number, expected_street_number)
        self.assertEqual(record.street_name, address_line1)

    # fmt: off
    @parameterized.expand([
        ('full_phone', 
         '1234567890',
         '123',
         '456',
         '7890'),
         
        ('partial_phone',
         '123456',
         '123',
         '456',
         ''),
         
        ('short_phone',
         '123',
         '123',
         '',
         ''),
         
        ('empty_phone',
         '',
         '',
         '',
         ''),
    ])
    # fmt: on
    def test_to_identified_account_phone_parsing(
        self,
        name: str,
        input_phone: str,
        expected_area: str,
        expected_exchange: str,
        expected_line: str
    ):
        record = InternalRecord(
            primaryPhone=input_phone,
            accountType=Description(description="Residential")
        )
        result = record.to_identified_account()
        
        self.assertEqual(result.phone_number.area_code, expected_area)
        self.assertEqual(result.phone_number.exchange, expected_exchange)
        self.assertEqual(result.phone_number.line_number, expected_line)

class TestOracleDESRecord(TestCase):
    
    # fmt: off
    @parameterized.expand([
        ('standard_name',
         'Doe, John',
         'John',
         'Doe'),
         
        ('comma_in_name',
         'O\'Connor, Mary',
         'Mary',
         'O\'Connor'),
         
        ('multiple_commas',
         'Smith, Jr., Bob',
         'Jr., Bob',
         'Smith'),
         
        ('empty_name',
         '',
         '',
         ''),
         
        ('no_comma',
         'John Smith',
         '',
         ''),
    ])
    # fmt: on
    def test_oracle_name_parsing(
        self,
        name: str,
        input_name: str,
        expected_first: str,
        expected_last: str
    ):
        record = OracleDESRecord(ACCT_NAME=input_name)
        
        self.assertEqual(record.first_name, expected_first)
        self.assertEqual(record.last_name, expected_last)

class TestGeneralRequest(TestCase):

    # fmt: off
    @parameterized.expand([
        ('complete_identifier',
         'John',
         'Doe',
         '1234567890',
         'john@example.com',
         '123',
         'Main St',
         'Apt 4B',
         'New York',
         'NY',
         '12345'),
         
        ('minimal_identifier',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         '',
         ''),
    ])
    # fmt: on
    def test_from_full_identifier(
        self,
        name: str,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        street_num: str,
        street_name: str,
        apt: str,
        city: str,
        state: str,
        zip_code: str
    ):
        # Create a mock FullIdentifier with all necessary nested objects
        mock_full_id = mock.Mock()
        mock_full_id.name.first_name = first_name
        mock_full_id.name.last_name = last_name
        mock_full_id.phone_number.ten_digits_only = phone
        mock_full_id.email = email
        mock_full_id.address.street_number = street_num
        mock_full_id.address.street_name = street_name
        mock_full_id.address.line2 = apt
        mock_full_id.address.city = city
        mock_full_id.address.state = state
        mock_full_id.address.simplified_postal_code = zip_code

        result = GeneralRequest.from_full_identifier(mock_full_id)
        
        self.assertEqual(result.first_name, first_name)
        self.assertEqual(result.last_name, last_name)
        self.assertEqual(result.phone_number, phone)
        self.assertEqual(result.email_address, email)
        self.assertEqual(result.street_number, street_num)
        self.assertEqual(result.street_name, street_name)
        self.assertEqual(result.apartment, apt)
        self.assertEqual(result.city, city)
        self.assertEqual(result.state, state)
        self.assertEqual(result.zipcode5, zip_code)

class TestIdentifiedAccount(TestCase):

    def test_default_values(self):
        account = IdentifiedAccount(
            name=mock.Mock(),
            phone_number=mock.Mock(),
            address=mock.Mock(),
            email=""
        )
        
        self.assertEqual(account.match_score, 0.0)
        self.assertEqual(account.account_type, "")
        self.assertEqual(account.status, "")
        self.assertEqual(account.source, "")
        self.assertEqual(account.ucan, "")
        self.assertEqual(account.billing_account_number, "")
        self.assertEqual(account.spectrum_core_account, "")
        self.assertEqual(account.spectrum_core_division, "")
