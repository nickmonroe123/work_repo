class AddressTests(TestCase):

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
