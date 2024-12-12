from django.test import TestCase
from identifiers.structs import Address, FullIdentifier, Name, PhoneNumber

class IdentifierTestCase(TestCase):
    def setUp(self):
        """Set up test data that will be used across multiple tests"""
        self.internal_record_data = {
            "primaryPhone": "1234567890",
            "firstName": "John",
            "lastName": "Doe",
            "zipCode5": "12345",
            "emailAddress": "john.doe@example.com",
            "streetNumber": "123",
            "streetName": "Main St",
            "city": "Springfield",
            "state": "IL",
            "line2": "Apt 4B",
            "uCAN": "ABC123",
            "divisionID": "DIV001",
            "accountStatus": "Active",
            "secondaryPhone": "9876543210",
            "accountNumber": "ACC001",
            "sourceMSO": "Source1",
            "addressLine1": "123 Main St",
            "addressLine2": "Apt 4B",
            "accountType": {"description": "Residential"}
        }

        self.oracle_record_data = {
            "ACCT_NUM": "ACC001",
            "PRIMARY_NUMBER": "1234567890",
            "secondaryPhone": "9876543210",
            "ACCT_NAME": "Doe, John",
            "PSTL_CD_TXT_BLR": "12345",
            "EMAIL_ADDR": "john.doe@example.com",
            "CITY_NM_BLR": "Springfield",
            "STATE_NM_BLR": "IL",
            "UCAN": "ABC123",
            "SPC_DIV_ID": "DIV001",
            "ACCOUNTSTATUS": "Active",
            "ACCT_TYPE_CD": "Residential",
            "SRC_SYS_CD": "Source1",
            "BLR_ADDR1_LINE": "123 Main St",
            "BLR_ADDR2_LINE": "Apt 4B"
        }

        self.full_identifier = FullIdentifier(
            name=Name(first_name="John", last_name="Doe"),
            phone_number=PhoneNumber(
                area_code="123",
                exchange="456",
                line_number="7890",
                extension="",
                type_code=""
            ),
            address=Address(
                city="Springfield",
                state="IL",
                line1="123 Main St",
                line2="Apt 4B",
                postal_code="12345"
            ),
            email="john.doe@example.com"
        )

class InternalRecordTests(IdentifierTestCase):
    def test_internal_record_creation(self):
        """Test creation of InternalRecord with all fields"""
        record = InternalRecord(**self.internal_record_data)
        
        self.assertEqual(record.phone_number, "1234567890")
        self.assertEqual(record.first_name, "John")
        self.assertEqual(record.last_name, "Doe")
        self.assertEqual(record.zipcode5, "12345")
        self.assertEqual(record.email_address, "john.doe@example.com")
        self.assertEqual(record.street_number, "123")
        self.assertEqual(record.street_name, "123 Main St")
        self.assertEqual(record.city, "Springfield")
        self.assertEqual(record.state, "IL")
        self.assertEqual(record.ucan, "ABC123")
        self.assertEqual(record.division_id, "DIV001")
        self.assertEqual(record.account_status, "Active")
        self.assertEqual(record.account_number, "ACC001")
        self.assertEqual(record.source, "Source1")
        self.assertEqual(record._address_line_1, "123 Main St")
        self.assertEqual(record._address_line_2, "Apt 4B")
        self.assertEqual(record.account_description, "Residential")

    def test_internal_record_full_address(self):
        """Test full address formatting with apartment"""
        record = InternalRecord(**self.internal_record_data)
        expected_full_address = "123 Main St Apt 4B Springfield IL"
        expected_full_address_no_apt = "123 Main St Springfield IL"
        
        self.assertEqual(record.full_address, expected_full_address)
        self.assertEqual(record.full_address_no_apt, expected_full_address_no_apt)

    def test_internal_record_no_apt(self):
        """Test full address formatting without apartment"""
        data = self.internal_record_data.copy()
        data["addressLine2"] = ""
        record = InternalRecord(**data)
        expected_full_address = "123 Main St Springfield IL"
        
        self.assertEqual(record.full_address, expected_full_address)
        self.assertFalse(hasattr(record, "full_address_no_apt"))

class OracleRecordTests(IdentifierTestCase):
    def test_oracle_record_creation(self):
        """Test creation of OracleDESRecord with all fields"""
        record = OracleDESRecord(**self.oracle_record_data)
        
        self.assertEqual(record.account_number, "ACC001")
        self.assertEqual(record.phone_number, "1234567890")
        self.assertEqual(record.first_name, "John")
        self.assertEqual(record.last_name, "Doe")
        self.assertEqual(record.zipcode5, "12345")
        self.assertEqual(record.email_address, "john.doe@example.com")
        self.assertEqual(record.city, "Springfield")
        self.assertEqual(record.state, "IL")
        self.assertEqual(record.ucan, "ABC123")
        self.assertEqual(record.division_id, "DIV001")
        self.assertEqual(record.account_status, "Active")
        self.assertEqual(record.source, "Source1")

    def test_oracle_record_name_parsing(self):
        """Test parsing of comma-separated names"""
        record = OracleDESRecord(**self.oracle_record_data)
        self.assertEqual(record.first_name, "John")
        self.assertEqual(record.last_name, "Doe")

    def test_oracle_record_invalid_name(self):
        """Test handling of invalid name format"""
        data = self.oracle_record_data.copy()
        data["ACCT_NAME"] = "Invalid Name Format"
        record = OracleDESRecord(**data)
        self.assertEqual(record.first_name, "")
        self.assertEqual(record.last_name, "")

class IdentifiedAccountConversionTests(IdentifierTestCase):
    def test_to_identified_account_internal(self):
        """Test conversion from InternalRecord to IdentifiedAccount"""
        record = InternalRecord(**self.internal_record_data)
        identified = record.to_identified_account()
        
        self.assertIsInstance(identified, IdentifiedAccount)
        self.assertEqual(identified.name.first_name, "John")
        self.assertEqual(identified.name.last_name, "Doe")
        self.assertEqual(identified.phone_number.area_code, "123")
        self.assertEqual(identified.phone_number.exchange, "456")
        self.assertEqual(identified.phone_number.line_number, "7890")
        self.assertEqual(identified.address.city, "Springfield")
        self.assertEqual(identified.address.state, "IL")
        self.assertEqual(identified.address.line1, "123 Main St")
        self.assertEqual(identified.address.line2, "Apt 4B")
        self.assertEqual(identified.address.postal_code, "12345")
        self.assertEqual(identified.email, "john.doe@example.com")
        self.assertEqual(identified.account_type, "Residential")
        self.assertEqual(identified.status, "Active")
        self.assertEqual(identified.source, "Source1")
        self.assertEqual(identified.ucan, "ABC123")
        self.assertEqual(identified.spectrum_core_account, "ACC001")
        self.assertEqual(identified.spectrum_core_division, "DIV001")

    def test_to_identified_account_oracle(self):
        """Test conversion from OracleDESRecord to IdentifiedAccount"""
        record = OracleDESRecord(**self.oracle_record_data)
        identified = record.to_identified_account()
        
        self.assertIsInstance(identified, IdentifiedAccount)
        self.assertEqual(identified.name.first_name, "John")
        self.assertEqual(identified.name.last_name, "Doe")
        self.assertEqual(identified.phone_number.area_code, "123")
        self.assertEqual(identified.phone_number.exchange, "456")
        self.assertEqual(identified.phone_number.line_number, "7890")
        self.assertEqual(identified.address.city, "Springfield")
        self.assertEqual(identified.address.state, "IL")
        self.assertEqual(identified.address.postal_code, "12345")

class GeneralRequestTests(IdentifierTestCase):
    def test_general_request_from_full_identifier(self):
        """Test creation of GeneralRequest from FullIdentifier"""
        request = GeneralRequest.from_full_identifier(self.full_identifier)
        
        self.assertEqual(request.phone_number, "1234567890")
        self.assertEqual(request.first_name, "John")
        self.assertEqual(request.last_name, "Doe")
        self.assertEqual(request.zipcode5, "12345")
        self.assertEqual(request.email_address, "john.doe@example.com")
        self.assertEqual(request.city, "Springfield")
        self.assertEqual(request.state, "IL")
        self.assertEqual(request.apartment, "Apt 4B")

class EdgeCaseTests(IdentifierTestCase):
    def test_empty_phone_number(self):
        """Test handling of empty phone numbers"""
        data = self.oracle_record_data.copy()
        data["PRIMARY_NUMBER"] = ""
        record = OracleDESRecord(**data)
        identified = record.to_identified_account()
        
        self.assertEqual(identified.phone_number.area_code, "")
        self.assertEqual(identified.phone_number.exchange, "")
        self.assertEqual(identified.phone_number.line_number, "")

    def test_partial_phone_number(self):
        """Test handling of partial phone numbers"""
        data = self.oracle_record_data.copy()
        data["PRIMARY_NUMBER"] = "123"
        record = OracleDESRecord(**data)
        identified = record.to_identified_account()
        
        self.assertEqual(identified.phone_number.area_code, "123")
        self.assertEqual(identified.phone_number.exchange, "")
        self.assertEqual(identified.phone_number.line_number, "")

    def test_empty_address(self):
        """Test handling of empty addresses"""
        data = self.oracle_record_data.copy()
        data["BLR_ADDR1_LINE"] = ""
        record = OracleDESRecord(**data)
        
        self.assertEqual(record.street_number, "")
        self.assertEqual(record.street_name, "")

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'test'])
