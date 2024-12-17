from unittest import TestCase
from unittest.mock import patch, MagicMock
import msgspec
from typing import Dict, List

class TestOracleDESProcess(TestCase):
    def setUp(self):
        self.account_process = AccountProcess()
        # Setup a complete valid request
        self.valid_request = GeneralRequest(
            phone_number="5551234567",
            first_name="John",
            last_name="Doe",
            zipcode5="62701",
            email_address="john.doe@example.com",
            street_number="123",
            street_name="Main St",
            city="Springfield",
            state="IL",
        )
        self.account_process.ext_request = self.valid_request

        # Setup mock record with properly formatted data
        self.mock_record = {
            "ACCT_NUM": "12345",
            "ACCT_NAME": "Doe, John",  # Format matches the expected "lastname, firstname"
            "PRIMARY_NUMBER": "5551234567",
            "EMAIL_ADDR": "john.doe@example.com",
            "CITY_NM_BLR": "Springfield",
            "STATE_NM_BLR": "IL",
            "PSTL_CD_TXT_BLR": "62701",
            "BLR_ADDR1_LINE": "123 Main St",
            "BLR_ADDR2_LINE": "Apt 4B",
            "ACCOUNTSTATUS": "Active",
            "ACCT_TYPE_CD": "RES",
            "SRC_SYS_CD": "BHN",
            "SPC_DIV_ID": "DIV123",
            "UCAN": "UCAN123",
        }

    @patch('oracledb.connect')
    def test_query_with_params_success(self, mock_connect):
        """Test successful query execution with parameters and verify OracleDESRecord structure."""
        # Setup cursor mock
        mock_cursor = MagicMock()
        mock_cursor.description = [(k,) for k in self.mock_record.keys()]
        mock_cursor.fetchall.return_value = [tuple(self.mock_record.values())]
        mock_cursor.__iter__.return_value = [tuple(self.mock_record.values())]
        
        # Setup connection mock
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        sql = "SELECT * FROM test_table"
        result = query_with_params(sql)

        # Verify basic execution
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], OracleDESRecord)

        # Get the first (and only) record
        record = result[0]

        # Test basic field mappings
        self.assertEqual(record.account_number, "12345")
        self.assertEqual(record.phone_number, "5551234567")
        self.assertEqual(record.email_address, "john.doe@example.com")
        self.assertEqual(record.city, "Springfield")
        self.assertEqual(record.state, "IL")
        self.assertEqual(record.zipcode5, "62701")
        self.assertEqual(record.account_status, "Active")
        self.assertEqual(record.account_description, "RES")
        self.assertEqual(record.source, "BHN")
        self.assertEqual(record.division_id, "DIV123")
        self.assertEqual(record.ucan, "UCAN123")

        # Test post_init processing
        # Verify name splitting
        self.assertEqual(record.first_name.strip(), "John")
        self.assertEqual(record.last_name.strip(), "Doe")

        # Verify address processing
        self.assertEqual(record._address_line_1, "123 Main St")
        self.assertEqual(record._address_line_2, "Apt 4B")
        self.assertEqual(record.street_number, "123")
        self.assertEqual(record.street_name, "123 Main St")

        # Verify full address construction
        expected_full_address = "123 Main St Apt 4B Springfield IL"
        expected_full_address_no_apt = "123 Main St Springfield IL"
        self.assertEqual(record.full_address, expected_full_address)
        self.assertEqual(record.full_address_no_apt, expected_full_address_no_apt)

        # Test conversion to IdentifiedAccount
        identified_account = record.to_identified_account()
        self.assertIsInstance(identified_account, IdentifiedAccount)
        
        # Verify IdentifiedAccount structure
        self.assertEqual(identified_account.name.first_name, "John")
        self.assertEqual(identified_account.name.last_name, "Doe")
        self.assertEqual(identified_account.phone_number.area_code, "555")
        self.assertEqual(identified_account.phone_number.exchange, "123")
        self.assertEqual(identified_account.phone_number.line_number, "4567")
        self.assertEqual(identified_account.address.city, "Springfield")
        self.assertEqual(identified_account.address.state, "IL")
        self.assertEqual(identified_account.address.line1, "123 Main St")
        self.assertEqual(identified_account.address.line2, "Apt 4B")
        self.assertEqual(identified_account.address.postal_code, "62701")
        self.assertEqual(identified_account.email, "john.doe@example.com")
        self.assertEqual(identified_account.account_type, "RES")
        self.assertEqual(identified_account.status, "Active")
        self.assertEqual(identified_account.source, "BHN")
        self.assertEqual(identified_account.ucan, "UCAN123")
        self.assertEqual(identified_account.spectrum_core_account, "12345")
        self.assertEqual(identified_account.spectrum_core_division, "DIV123")

    @patch('oracledb.connect')
    def test_query_with_params_missing_address_line2(self, mock_connect):
        """Test processing when address line 2 is empty."""
        modified_record = self.mock_record.copy()
        modified_record["BLR_ADDR2_LINE"] = ""
        
        # Setup cursor mock
        mock_cursor = MagicMock()
        mock_cursor.description = [(k,) for k in modified_record.keys()]
        mock_cursor.fetchall.return_value = [tuple(modified_record.values())]
        mock_cursor.__iter__.return_value = [tuple(modified_record.values())]
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        result = query_with_params("SELECT * FROM test_table")
        record = result[0]

        # Verify address handling with empty line2
        expected_full_address = "123 Main St Springfield IL"
        self.assertEqual(record.full_address, expected_full_address)
        self.assertEqual(record.full_address_no_apt, "")  # Should be empty when no apt
