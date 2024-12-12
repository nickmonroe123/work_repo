from django.test import TestCase
import re
from typing import Any
import unittest

# Assuming the above classes are in a module called 'identifiers'
from .identifiers import Name, PhoneNumber, Address, FullIdentifier

class NameTests(TestCase):
    def test_basic_name(self):
        """Test basic name with required fields only"""
        name = Name(first_name="John", last_name="Doe")
        self.assertEqual(name.first_name, "John")
        self.assertEqual(name.last_name, "Doe")
        self.assertEqual(name.middle_name, "")
        self.assertEqual(name.prefix, "")
        self.assertEqual(name.suffix, "")

    def test_full_name(self):
        """Test name with all fields populated"""
        name = Name(
            first_name="John",
            last_name="Doe",
            middle_name="William",
            prefix="Dr.",
            suffix="Jr."
        )
        self.assertEqual(name.first_name, "John")
        self.assertEqual(name.last_name, "Doe")
        self.assertEqual(name.middle_name, "William")
        self.assertEqual(name.prefix, "Dr.")
        self.assertEqual(name.suffix, "Jr.")

class PhoneNumberTests(TestCase):
    def test_empty_phone(self):
        """Test phone number with no fields populated"""
        phone = PhoneNumber()
        self.assertEqual(phone.ten_digits_only, "")
        
    def test_basic_phone(self):
        """Test phone with just the required 10-digit fields"""
        phone = PhoneNumber(
            area_code="123",
            exchange="456",
            line_number="7890"
        )
        self.assertEqual(phone.ten_digits_only, "1234567890")

    def test_full_phone(self):
        """Test phone with all fields populated"""
        phone = PhoneNumber(
            country_code="1",
            area_code="123",
            exchange="456",
            line_number="7890",
            extension="123",
            type_code="HOME"
        )
        self.assertEqual(phone.ten_digits_only, "1234567890")

    def test_phone_with_formatting(self):
        """Test phone number with various formatting characters"""
        phone = PhoneNumber(
            area_code="(123)",
            exchange="456-",
            line_number=" 7890"
        )
        self.assertEqual(phone.ten_digits_only, "1234567890")

    def test_phone_shorter_than_ten_digits(self):
        """Test phone number with fewer than 10 digits"""
        phone = PhoneNumber(
            area_code="12",
            exchange="34",
            line_number="56"
        )
        self.assertEqual(phone.ten_digits_only, "0000123456")

    def test_phone_longer_than_ten_digits(self):
        """Test phone number with more than 10 digits"""
        phone = PhoneNumber(
            area_code="9123",
            exchange="4567",
            line_number="89012"
        )
        self.assertEqual(phone.ten_digits_only, "1234567890")

class AddressTests(TestCase):
    def test_basic_address(self):
        """Test address with required fields only"""
        address = Address(
            city="Springfield",
            state="IL",
            line1="123 Main St",
            postal_code="62701"
        )
        self.assertEqual(address.city, "Springfield")
        self.assertEqual(address.state, "IL")
        self.assertEqual(address.line1, "123 Main St")
        self.assertEqual(address.postal_code, "62701")
        self.assertEqual(address.line2, "")
        self.assertEqual(address.country_code, "")

    def test_full_address(self):
        """Test address with all fields populated"""
        address = Address(
            city="Springfield",
            state="IL",
            line1="123 Main St",
            line2="Apt 4B",
            postal_code="62701-1234",
            country_code="US"
        )
        self.assertEqual(address.city, "Springfield")
        self.assertEqual(address.state, "IL")
        self.assertEqual(address.line1, "123 Main St")
        self.assertEqual(address.line2, "Apt 4B")
        self.assertEqual(address.postal_code, "62701-1234")
        self.assertEqual(address.country_code, "US")
        self.assertEqual(address.simplified_postal_code, "62701")

    def test_street_parsing_scenarios(self):
        """Test various street address parsing scenarios"""
        test_cases = [
            # Standard format
            {
                "input": "123 Main Street",
                "expected_number": "123",
                "expected_name": "Main Street"
            },
            # No street number
            {
                "input": "Main Street",
                "expected_number": "",
                "expected_name": "Main Street"
            },
            # Complex street number
            {
                "input": "123-A Main Street",
                "expected_number": "123-A",
                "expected_name": "Main Street"
            },
            # Extra spaces
            {
                "input": "  123   Main   Street  ",
                "expected_number": "123",
                "expected_name": "Main   Street"
            },
            # Empty string
            {
                "input": "",
                "expected_number": "",
                "expected_name": ""
            },
            # Just spaces
            {
                "input": "   ",
                "expected_number": "",
                "expected_name": ""
            },
            # Complex address with unit
            {
                "input": "123B Main Street Unit 4",
                "expected_number": "123B",
                "expected_name": "Main Street Unit 4"
            },
            # Street number with hyphens and letters
            {
                "input": "123-45B Main Street",
                "expected_number": "123-45B",
                "expected_name": "Main Street"
            }
        ]

        for case in test_cases:
            address = Address(
                city="Test City",
                state="TS",
                line1=case["input"],
                postal_code="12345"
            )
            self.assertEqual(address.street_number, case["expected_number"])
            self.assertEqual(address.street_name, case["expected_name"])

    def test_postal_code_parsing(self):
        """Test various postal code formats"""
        test_cases = [
            ("12345", "12345"),
            ("12345-6789", "12345"),
            ("12345-", "12345"),
            ("-12345", ""),
            ("", ""),
            ("12345-6789-0000", "12345")
        ]

        for postal_code, expected in test_cases:
            address = Address(
                city="Test City",
                state="TS",
                line1="123 Test St",
                postal_code=postal_code
            )
            self.assertEqual(address.simplified_postal_code, expected)

class FullIdentifierTests(TestCase):
    def setUp(self):
        """Set up basic test data"""
        self.basic_name = Name(
            first_name="John",
            last_name="Doe"
        )
        self.basic_phone = PhoneNumber(
            area_code="123",
            exchange="456",
            line_number="7890"
        )
        self.basic_address = Address(
            city="Springfield",
            state="IL",
            line1="123 Main St",
            postal_code="62701"
        )

    def test_basic_identifier(self):
        """Test basic identifier with minimal required fields"""
        identifier = FullIdentifier(
            name=self.basic_name,
            phone_number=self.basic_phone,
            address=self.basic_address,
            email="john.doe@example.com"
        )
        self.assertEqual(identifier.email, "john.doe@example.com")
        self.assertEqual(identifier.name.first_name, "John")
        self.assertEqual(identifier.phone_number.ten_digits_only, "1234567890")
        self.assertEqual(identifier.address.city, "Springfield")

    def test_full_identifier(self):
        """Test identifier with all fields populated"""
        full_name = Name(
            first_name="John",
            last_name="Doe",
            middle_name="William",
            prefix="Dr.",
            suffix="Jr."
        )
        full_phone = PhoneNumber(
            country_code="1",
            area_code="123",
            exchange="456",
            line_number="7890",
            extension="123",
            type_code="HOME"
        )
        full_address = Address(
            city="Springfield",
            state="IL",
            line1="123 Main St",
            line2="Apt 4B",
            postal_code="62701-1234",
            country_code="US"
        )
        
        identifier = FullIdentifier(
            name=full_name,
            phone_number=full_phone,
            address=full_address,
            email="john.w.doe.jr@example.com"
        )
        
        # Verify all fields are correctly set
        self.assertEqual(identifier.name.prefix, "Dr.")
        self.assertEqual(identifier.name.first_name, "John")
        self.assertEqual(identifier.name.middle_name, "William")
        self.assertEqual(identifier.name.last_name, "Doe")
        self.assertEqual(identifier.name.suffix, "Jr.")
        
        self.assertEqual(identifier.phone_number.country_code, "1")
        self.assertEqual(identifier.phone_number.ten_digits_only, "1234567890")
        self.assertEqual(identifier.phone_number.extension, "123")
        self.assertEqual(identifier.phone_number.type_code, "HOME")
        
        self.assertEqual(identifier.address.street_number, "123")
        self.assertEqual(identifier.address.street_name, "Main St")
        self.assertEqual(identifier.address.line2, "Apt 4B")
        self.assertEqual(identifier.address.city, "Springfield")
        self.assertEqual(identifier.address.state, "IL")
        self.assertEqual(identifier.address.postal_code, "62701-1234")
        self.assertEqual(identifier.address.simplified_postal_code, "62701")
        self.assertEqual(identifier.address.country_code, "US")
        
        self.assertEqual(identifier.email, "john.w.doe.jr@example.com")
