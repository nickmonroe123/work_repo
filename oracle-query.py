from django.test import TestCase
from unittest.mock import Mock, patch
from account_identification.structs import *
from identifiers.structs import *
from services import AccountProcess

class TestAccountProcess(TestCase):
    def setUp(self):
        """Set up test data before each test method."""
        self.account_process = AccountProcess()
        # Set up basic ext_request data that many functions need
        self.account_process.ext_request = GeneralRequest()
        self.account_process.ext_request.phone_number = "1234567890"
        self.account_process.ext_request.first_name = "John"
        self.account_process.ext_request.last_name = "Doe"
        self.account_process.ext_request.zipcode5 = "12345"
        self.account_process.ext_request.email_address = "test@example.com"
        self.account_process.ext_request.street_number = "123"
        self.account_process.ext_request.street_name = "Main St"
        self.account_process.ext_request.city = "Anytown"
        self.account_process.ext_request.state = "CA"
        
    def create_test_full_identifier(
        self,
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

    def test_phone_parse(self):
        """Test phone number parsing functionality"""
        # Test standard phone number
        phone = PhoneNumber(
            country_code="1", area_code="555", exchange="123", line_number="4567"
        )
        self.assertEqual(self.account_process.phone_parse(phone), "5551234567")

        # Test phone number with formatting
        phone_formatted = PhoneNumber(
            country_code="1", area_code="(555)", exchange="123", line_number="4567"
        )
        self.assertEqual(self.account_process.phone_parse(phone_formatted), "5551234567")

        # Test incomplete phone number
        phone_incomplete = PhoneNumber(area_code="555", line_number="4567")
        self.assertEqual(self.account_process.phone_parse(phone_incomplete), "5554567")

        # Test empty phone number
        phone_empty = PhoneNumber()
        self.assertEqual(self.account_process.phone_parse(phone_empty), "")

    def test_zip_name_parse(self):
        """Test zip code and name parsing functionality"""
        # Standard case
        full_id = self.create_test_full_identifier(
            first_name="John", last_name="Doe", postal_code="12345"
        )
        first_name, last_name, zipcode = self.account_process.zip_name_parse(full_id)
        self.assertEqual(first_name, "John")
        self.assertEqual(last_name, "Doe")
        self.assertEqual(zipcode, "12345")

        # Postal code with extended zip
        full_id_extended = self.create_test_full_identifier(
            first_name="Jane", last_name="Smith", postal_code="12345-6789"
        )
        first_name, last_name, zipcode = self.account_process.zip_name_parse(full_id_extended)
        self.assertEqual(first_name, "Jane")
        self.assertEqual(last_name, "Smith")
        self.assertEqual(zipcode, "12345")

        # Empty name and postal code
        full_id_empty = FullIdentifier(
            name=Name(first_name="", last_name=""),
            phone_number=PhoneNumber(),
            address=Address(city="", state="", line1="", postal_code=""),
            email="",
        )
        first_name, last_name, zipcode = self.account_process.zip_name_parse(full_id_empty)
        self.assertEqual(first_name, "")
        self.assertEqual(last_name, "")
        self.assertEqual(zipcode, "")

    def test_address_parse(self):
        """Test address parsing functionality"""
        # Standard address
        address = Address(
            line1="123 Main St",
            city="Anytown",
            state="NY",
            line2="Apt 4B",
            postal_code="62323",
        )
        street_number, street_name, city, state, apartment = self.account_process.address_parse(
            address
        )
        self.assertEqual(street_number, "123")
        self.assertEqual(street_name, "Main St")
        self.assertEqual(city, "Anytown")
        self.assertEqual(state, "NY")
        self.assertEqual(apartment, "Apt 4B")

        # Address without apartment
        address_no_apt = Address(
            line1="456 Oak Rd", city="Smallville", state="CA", postal_code="62323"
        )
        street_number, street_name, city, state, apartment = self.account_process.address_parse(
            address_no_apt
        )
        self.assertEqual(street_number, "456")
        self.assertEqual(street_name, "Oak Rd")
        self.assertEqual(city, "Smallville")
        self.assertEqual(state, "CA")
        self.assertEqual(apartment, "")

    def test_address_missing_fields(self):
        """Test address parsing with missing required fields"""
        with self.assertRaises(TypeError):
            Address(line1="123 Main St", city="Anytown", state="NY", line2="Apt 4B")

        with self.assertRaises(TypeError):
            Address(line1="123 Main St", state="NY", line2="Apt 4B", postal_code="62323")

        with self.assertRaises(TypeError):
            Address(city="Anytown", state="NY", line2="Apt 4B", postal_code="62323")

        with self.assertRaises(TypeError):
            Address(line1="123 Main St", city="Anytown", line2="Apt 4B", postal_code="62323")

    def test_address_edge_cases(self):
        """Test edge cases for address parsing"""
        # Street name without number
        address_no_number = Address(
            line1="Broadway", city="New York", state="NY", postal_code="62323"
        )
        street_number, street_name, city, state, apartment = self.account_process.address_parse(
            address_no_number
        )
        self.assertEqual(street_number, "")
        self.assertEqual(street_name, "Broadway")
        self.assertEqual(city, "New York")
        self.assertEqual(state, "NY")
        self.assertEqual(apartment, "")

        # Street number without name
        address_only_number = Address(
            line1="756", city="New York", state="NY", postal_code="62323"
        )
        street_number, street_name, city, state, apartment = self.account_process.address_parse(
            address_only_number
        )
        self.assertEqual(street_number, "756")
        self.assertEqual(street_name, "")

    def test_ext_request_init(self):
        """Test external request initialization"""
        # Full identifier with complete information
        full_id = self.create_test_full_identifier()
        self.account_process.ext_request_init(full_id)

        self.assertEqual(self.account_process.ext_request.phone_number, "5551234567")
        self.assertEqual(self.account_process.ext_request.first_name, "John")
        self.assertEqual(self.account_process.ext_request.last_name, "Doe")
        self.assertEqual(self.account_process.ext_request.zipcode5, "12345")
        self.assertEqual(self.account_process.ext_request.email_address, "john.doe@example.com")
        self.assertEqual(self.account_process.ext_request.street_number, "123")
        self.assertEqual(self.account_process.ext_request.street_name, "Main St")
        self.assertEqual(self.account_process.ext_request.city, "Anytown")
        self.assertEqual(self.account_process.ext_request.state, "NY")

        # Minimal identifier
        minimal_id = FullIdentifier(
            name=Name(first_name="Minimal", last_name="User"),
            phone_number=PhoneNumber(),
            address=Address(city="", state="", line1="", postal_code=""),
            email="",
        )
        self.account_process.ext_request_init(minimal_id)
        self.assertEqual(self.account_process.ext_request.first_name, "Minimal")
        self.assertEqual(self.account_process.ext_request.last_name, "User")

    def test_error_handling(self):
        """Test error handling in full search"""
        invalid_id = FullIdentifier(
            name=Name(first_name="", last_name=""),
            phone_number=PhoneNumber(),
            address=Address(city="", state="", line1="", postal_code=""),
            email="",
        )
        with self.assertRaises(Exception):
            with patch('logging.info') as mock_logger:
                self.account_process.full_search(invalid_id)
                self.assertGreater(mock_logger.call_count, 0)

    def test_comprehensive_full_identifier_processing(self):
        """Test comprehensive cases for full identifier processing"""
        test_cases = [
            # Standard full name
            self.create_test_full_identifier(first_name="John", last_name="Doe"),
            # Unicode names
            self.create_test_full_identifier(first_name="José", last_name="García"),
            # Very long names
            self.create_test_full_identifier(first_name="A" * 50, last_name="B" * 50),
            # Just name
            FullIdentifier(
                name=Name(first_name="Mini", last_name="User"),
                phone_number=PhoneNumber(),
                address=Address(city="", state="", line1="", postal_code=""),
                email="",
            ),
            # Just phone
            FullIdentifier(
                name=Name(first_name="", last_name=""),
                phone_number=PhoneNumber(
                    area_code="555", exchange="666", line_number="7777"
                ),
                address=Address(city="", state="", line1="", postal_code=""),
                email="",
            ),
            # International address
            self.create_test_full_identifier(
                street_line1="789 International St",
                city="Toronto",
                state="ON",
                postal_code="M5V 2T6",
            ),
        ]

        for test_input in test_cases:
            try:
                results = self.account_process.full_search(test_input)
                if results:
                    for result in results:
                        self.assertIsNone(results) or self.assertIsInstance(
                            result, IdentifiedAccount
                        )
            except Exception as e:
                self.fail(f"Unexpected error in processing: {e}")

    def test_phone_search_invalid_number(self):
        """Test phone search with invalid phone number"""
        self.account_process.core_services_list = []
        self.account_process.ext_request.phone_number = "123"  # Invalid length
        self.account_process.phone_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_name_zip_search_invalid_data(self):
        """Test name and zip search with invalid data"""
        self.account_process.core_services_list = []
        self.account_process.ext_request.zipcode5 = "1234"  # Invalid length
        self.account_process.name_zip_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_email_search_empty_email(self):
        """Test email search with empty email"""
        self.account_process.core_services_list = []
        self.account_process.ext_request.email_address = ""
        self.account_process.email_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_clean_address_search(self):
        """Test clean address search functionality"""
        # Test matching apartment
        json_list = [{'addressLine2': 'Apt 123', 'addressLine1': '123 Main St'}]
        self.account_process.ext_request.apartment = 'Apt 123'
        result = self.account_process.clean_address_search(json_list)
        self.assertEqual(len(result), 1)

        # Test non-matching apartment
        json_list = [{'addressLine2': 'Apt 456', 'addressLine1': '123 Main St'}]
        result = self.account_process.clean_address_search(json_list)
        self.assertEqual(len(result), 0)

    def test_billing_search_invalid_data(self):
        """Test billing search with invalid data"""
        self.account_process.core_services_list = []
        self.account_process.ext_request.last_name = ""
        self.account_process.billing_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    @patch('models.search_with_phone')
    @patch('models.search_with_address')
    @patch('models.search_with_email')
    @patch('models.search_with_zip_name')
    def test_oracle_des_process_failed_queries(
        self, mock_zip_name, mock_email, mock_address, mock_phone
    ):
        """Test oracle DES process with failed queries"""
        mock_phone.side_effect = Exception("DB Error")
        mock_address.side_effect = Exception("DB Error")
        mock_email.side_effect = Exception("DB Error")
        mock_zip_name.side_effect = Exception("DB Error")

        self.account_process.oracle_des_process()
        self.assertEqual(len(self.account_process.oracle_des_list), 0)
