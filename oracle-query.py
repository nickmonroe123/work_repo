from parameterized import parameterized
from unittest import TestCase

class AddressTests(TestCase):

    # fmt: off
    @parameterized.expand([
        # name, input, expected_number, expected_name
        ('standard_format', 
         "123 Main Street", 
         "123", 
         "Main Street"),
        
        ('no_street_number',
         "Main Street",
         "",
         "Main Street"),
         
        ('complex_street_number',
         "123-A Main Street",
         "123-A",
         "Main Street"),
         
        ('extra_spaces',
         "  123   Main   Street  ",
         "123",
         "Main   Street"),
         
        ('empty_string',
         "",
         "",
         ""),
         
        ('just_spaces',
         "   ",
         "",
         ""),
         
        ('complex_address_with_unit',
         "123B Main Street Unit 4",
         "123B",
         "Main Street Unit 4"),
         
        ('street_number_with_hyphens',
         "123-45B Main Street",
         "123-45B",
         "Main Street"),
    ])
    # fmt: on
    def test_street_parsing_scenarios(
        self, name, input_address, expected_number, expected_name
    ):
        """Test various street address parsing scenarios"""
        address = Address(
            city="Test City",
            state="TS",
            line1=input_address,
            postal_code="12345"
        )
        self.assertEqual(address.street_number, expected_number)
        self.assertEqual(address.street_name, expected_name)

    # fmt: off
    @parameterized.expand([
        ('standard_zip', "12345", "12345"),
        ('zip_plus_four', "12345-6789", "12345"),
        ('zip_with_hyphen', "12345-", "12345"),
        ('invalid_hyphen_prefix', "-12345", ""),
        ('empty_postal', "", ""),
        ('extended_zip', "12345-6789-0000", "12345"),
    ])
    # fmt: on
    def test_postal_code_parsing(
        self, name, postal_code, expected
    ):
        """Test various postal code formats"""
        address = Address(
            city="Test City",
            state="TS",
            line1="123 Test St",
            postal_code=postal_code
        )
        self.assertEqual(address.simplified_postal_code, expected)
