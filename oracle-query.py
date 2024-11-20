import unittest
from unittest.mock import patch, MagicMock
import json
import os
from typing import Dict, Any
import re
import pytest
from dataclasses import asdict

from .account_process import AccountProcessView
from .structs import GeneralRequest, InternalRecord, OracleDESRecord

class TestAccountProcessView(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.view = AccountProcessView()
        self.maxDiff = None
        
        # Sample valid input data
        self.valid_input = {
            "familyName": "SMITH",
            "givenName": "JOHN",
            "city": "WOODLAND HILLS",
            "line1": "6201 JACKIE AVE",
            "postalCode": "91367",
            "territoryCode": "CA",
            "line2": "",
            "areaCode": "637",
            "exchange": "123",
            "lineNumber": "4997",
            "emailAddress": "test@charter.com"
        }
        
        # Sample invalid input data
        self.invalid_input = {
            "familyName": "",
            "givenName": "",
            "city": "",
            "line1": "",
            "postalCode": "",
            "territoryCode": "",
            "areaCode": "",
            "exchange": "",
            "lineNumber": "",
            "emailAddress": ""
        }

    def test_environment_urls(self):
        """Test URL configuration based on environment."""
        test_cases = [
            ('prod', 'https://spectrumcore.charter.com/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1'),
            ('uat', 'https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1'),
            ('local', 'https://spectrumcoreuat.charter.com/spectrum-core/services/account/ept/getSpcAccountDivisionV1x1')
        ]
        
        for env, expected_url in test_cases:
            with patch.dict(os.environ, {'ENVIRONMENT': env}):
                view = AccountProcessView()
                self.assertEqual(view.url, expected_url)
                self.assertEqual(view.system_id, "ComplianceService")

    def test_phone_parse(self):
        """Test phone number parsing with various inputs."""
        test_cases = [
            # Valid cases
            ({
                "areaCode": "637",
                "exchange": "123",
                "lineNumber": "4997"
            }, ('', '6371234997')),
            
            # International number
            ({
                "areaCode": "1637",
                "exchange": "123",
                "lineNumber": "4997"
            }, ('1', '6371234997')),
            
            # Invalid cases
            ({}, ('', '')),  # Empty dict
            ({"areaCode": ""}, ('', '')),  # Missing fields
            ({"areaCode": "abc"}, ('', '')),  # Non-numeric
            
            # Edge cases
            ({
                "areaCode": "000",
                "exchange": "000",
                "lineNumber": "0000"
            }, ('', '0000000000')),
        ]
        
        for input_data, expected in test_cases:
            result = self.view.phone_parse(input_data)
            self.assertEqual(result, expected)

    def test_zip_name_parse(self):
        """Test name and zip code parsing."""
        test_cases = [
            # Valid case
            ({
                "postalCode": "91367",
                "givenName": "JOHN",
                "familyName": "SMITH"
            }, ("JOHN", "SMITH", "91367")),
            
            # Missing fields
            ({}, ('', '', '')),
            
            # Empty fields
            ({
                "postalCode": "",
                "givenName": "",
                "familyName": ""
            }, ('', '', '')),
            
            # Special characters in names
            ({
                "postalCode": "91367",
                "givenName": "JOHN-PAUL",
                "familyName": "O'SMITH"
            }, ("JOHN-PAUL", "O'SMITH", "91367")),
        ]
        
        for input_data, expected in test_cases:
            result = self.view.zip_name_parse(input_data)
            self.assertEqual(result, expected)

    def test_email_parse(self):
        """Test email parsing."""
        test_cases = [
            ({"emailAddress": "test@charter.com"}, "test@charter.com"),
            ({"emailAddress": ""}, ""),
            ({}, ""),
            ({"emailAddress": None}, ""),
            ({"wrong_key": "test@charter.com"}, ""),
        ]
        
        for input_data, expected in test_cases:
            result = self.view.email_parse(input_data)
            self.assertEqual(result, expected)

    def test_address_parse(self):
        """Test address parsing."""
        test_cases = [
            # Valid case
            ({
                "line1": "6201 JACKIE AVE",
                "city": "WOODLAND HILLS",
                "territoryCode": "CA"
            }, ("6201", "JACKIE AVE", "WOODLAND HILLS", "CA")),
            
            # Missing fields
            ({}, ('', '', '', '')),
            
            # Empty fields
            ({
                "line1": "",
                "city": "",
                "territoryCode": ""
            }, ('', '', '', '')),
            
            # Complex street address
            ({
                "line1": "123 MAIN STREET WEST",
                "city": "ANYTOWN",
                "territoryCode": "NY"
            }, ("123", "MAIN STREET WEST", "ANYTOWN", "NY")),
        ]
        
        for input_data, expected in test_cases:
            result = self.view.address_parse(input_data)
            self.assertEqual(result, expected)

    @patch('logging.getLogger')
    def test_post_method(self, mock_logger):
        """Test the post method with various scenarios."""
        test_cases = [
            (self.valid_input, []),  # Expecting empty list as core_services_list is not modified
            (self.invalid_input, []),
            ({}, []),  # Empty input
        ]
        
        for input_data, expected in test_cases:
            result = self.view.post(input_data)
            self.assertEqual(result, expected)
            # Verify logging calls
            mock_logger.return_value.info.assert_any_call('This is the start of a new account identification process.')

    def test_bad_phone_numbers(self):
        """Test handling of known bad phone numbers."""
        for bad_number in self.view.bad_numbers:
            input_data = self.valid_input.copy()
            input_data.update({
                "areaCode": bad_number[:3],
                "exchange": bad_number[3:6],
                "lineNumber": bad_number[6:]
            })
            result = self.view.post(input_data)
            self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
