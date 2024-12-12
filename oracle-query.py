from django.test import TestCase
from .structs import (
    IdentifiedAccount,
    GeneralRequest,
    InternalRecord,
    OracleDESRecord,
    Description,
    FullIdentifier,
    Name,
    PhoneNumber,
    Address,
)


class IdentifierTestCase(TestCase):
    def setUp(self):
        """Set up test data that will be used across multiple tests."""
        self.test_full_identifier = FullIdentifier(
            name=Name(
                first_name="John",
                last_name="Doe",
                middle_name="Robert",
            ),
            phone_number=PhoneNumber(
                area_code="555",
                exchange="123",
                line_number="4567",
            ),
            address=Address(
                line1="123 Main Street",
                line2="Apt 4B",
                city="Springfield",
                state="IL",
                postal_code="62701-1234",
            ),
            email="john.doe@example.com"
        )

    def test_general_request_from_full_identifier(self):
        """Test the conversion from FullIdentifier to GeneralRequest."""
        general_request = GeneralRequest.from_full_identifier(self.test_full_identifier)
        
        self.assertEqual(general_request.phone_number, "5551234567")
        self.assertEqual(general_request.first_name, "John")
        self.assertEqual(general_request.last_name, "Doe")
        self.assertEqual(general_request.zipcode5, "62701")
        self.assertEqual(general_request.email_address, "john.doe@example.com")
        self.assertEqual(general_request.street_number, "123")
        self.assertEqual(general_request.street_name, "Main Street")
        self.assertEqual(general_request.city, "Springfield")
        self.assertEqual(general_request.state, "IL")
        self.assertEqual(general_request.apartment, "Apt 4B")


class InternalRecordTestCase(TestCase):
    def setUp(self):
        """Set up test data for InternalRecord tests."""
        self.internal_record = InternalRecord(
            _address_line_1="123 Main Street",
            _address_line_2="Apt 4B",
            city="Springfield",
            state="IL",
            first_name="John",
            last_name="Doe",
            phone_number="5551234567",
            zipcode5="62701",
            email_address="john.doe@example.com",
            ucan="UC123",
            division_id="DIV456",
            account_status="ACTIVE",
            account_number="ACC789",
            source="SPECTRUM",
            _account_type=Description(description="RESIDENTIAL")
        )

    def test_post_init_processing(self):
        """Test the post-initialization processing of InternalRecord."""
        self.assertEqual(self.internal_record.street_number, "123")
        self.assertEqual(self.internal_record.street_name, "123 Main Street")
        self.assertEqual(
            self.internal_record.full_address,
            "123 Main Street Apt 4B Springfield IL"
        )
        self.assertEqual(
            self.internal_record.full_address_no_apt,
            "123 Main Street Springfield IL"
        )

    def test_to_identified_account(self):
        """Test conversion from InternalRecord to IdentifiedAccount."""
        identified = self.internal_record.to_identified_account()
        
        self.assertEqual(identified.name.first_name, "John")
        self.assertEqual(identified.name.last_name, "Doe")
        self.assertEqual(identified.phone_number.area_code, "555")
        self.assertEqual(identified.phone_number.exchange, "123")
        self.assertEqual(identified.phone_number.line_number, "4567")
        self.assertEqual(identified.address.line1, "123 Main Street")
        self.assertEqual(identified.address.line2, "Apt 4B")
        self.assertEqual(identified.account_type, "RESIDENTIAL")
        self.assertEqual(identified.status, "ACTIVE")
        self.assertEqual(identified.source, "SPECTRUM")
        self.assertEqual(identified.ucan, "UC123")
        self.assertEqual(identified.spectrum_core_account, "ACC789")
        self.assertEqual(identified.spectrum_core_division, "DIV456")


class OracleDESRecordTestCase(TestCase):
    def setUp(self):
        """Set up test data for OracleDESRecord tests."""
        self.oracle_record = OracleDESRecord(
            ACCT_NUM="ACC123",
            PRIMARY_NUMBER="5551234567",
            ACCT_NAME="Doe, John",
            PSTL_CD_TXT_BLR="62701",
            EMAIL_ADDR="john.doe@example.com",
            CITY_NM_BLR="Springfield",
            STATE_NM_BLR="IL",
            BLR_ADDR1_LINE="123 Main Street",
            BLR_ADDR2_LINE="Apt 4B",
            UCAN="UC123",
            SPC_DIV_ID="DIV456",
            ACCOUNTSTATUS="ACTIVE",
            ACCT_TYPE_CD="RESIDENTIAL",
            SRC_SYS_CD="ORACLE"
        )

    def test_post_init_name_parsing(self):
        """Test the post-initialization name parsing of OracleDESRecord."""
        self.assertEqual(self.oracle_record.first_name, "John")
        self.assertEqual(self.oracle_record.last_name, "Doe")

    def test_post_init_address_processing(self):
        """Test the post-initialization address processing of OracleDESRecord."""
        self.assertEqual(self.oracle_record.street_number, "123")
        self.assertEqual(self.oracle_record.street_name, "123 Main Street")
        self.assertEqual(
            self.oracle_record.full_address,
            "123 Main Street Apt 4B Springfield IL"
        )
        self.assertEqual(
            self.oracle_record.full_address_no_apt,
            "123 Main Street Springfield IL"
        )

    def test_to_identified_account(self):
        """Test conversion from OracleDESRecord to IdentifiedAccount."""
        identified = self.oracle_record.to_identified_account()
        
        self.assertEqual(identified.name.first_name, "John")
        self.assertEqual(identified.name.last_name, "Doe")
        self.assertEqual(identified.phone_number.area_code, "555")
        self.assertEqual(identified.phone_number.exchange, "123")
        self.assertEqual(identified.phone_number.line_number, "4567")
        self.assertEqual(identified.address.line1, "123 Main Street")
        self.assertEqual(identified.address.line2, "Apt 4B")
        self.assertEqual(identified.email, "john.doe@example.com")
        self.assertEqual(identified.account_type, "RESIDENTIAL")
        self.assertEqual(identified.status, "ACTIVE")
        self.assertEqual(identified.source, "ORACLE")
        self.assertEqual(identified.ucan, "UC123")
        self.assertEqual(identified.spectrum_core_account, "ACC123")
        self.assertEqual(identified.spectrum_core_division, "DIV456")


class EdgeCaseTestCase(TestCase):
    def test_internal_record_empty_address(self):
        """Test InternalRecord with empty address fields."""
        record = InternalRecord(
            _address_line_1="",
            city="Springfield",
            state="IL"
        )
        self.assertEqual(record.street_number, "")
        self.assertEqual(record.street_name, "")
        self.assertEqual(record.full_address, " Springfield IL")

    def test_oracle_record_malformed_name(self):
        """Test OracleDESRecord with malformed name field."""
        record = OracleDESRecord(ACCT_NAME="Single Name")
        self.assertEqual(record.first_name, "")
        self.assertEqual(record.last_name, "")

    def test_general_request_empty_phone(self):
        """Test GeneralRequest with empty phone number."""
        full_id = FullIdentifier(
            name=Name(first_name="John", last_name="Doe"),
            phone_number=PhoneNumber(),
            address=Address(
                line1="123 Main St",
                city="Springfield",
                state="IL",
                postal_code="62701"
            ),
            email=""
        )
        request = GeneralRequest.from_full_identifier(full_id)
        self.assertEqual(request.phone_number, "")

    def test_internal_record_missing_account_type(self):
        """Test InternalRecord with missing account type."""
        record = InternalRecord()
        identified = record.to_identified_account()
        self.assertEqual(identified.account_type, "")

    def test_oracle_record_empty_address_line2(self):
        """Test OracleDESRecord with empty address line 2."""
        record = OracleDESRecord(
            BLR_ADDR1_LINE="123 Main Street",
            CITY_NM_BLR="Springfield",
            STATE_NM_BLR="IL"
        )
        self.assertEqual(
            record.full_address,
            "123 Main Street Springfield IL"
        )
