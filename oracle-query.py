Ah, I see the issue. The problem is likely in how we're setting up the mock data and cursor. Let me fix that to ensure the data is being properly returned.



<function_calls>
<invoke name="artifacts">
<parameter name="id">test-query-params-fixed</parameter>
<parameter name="type">application/vnd.ant.code</parameter>
<parameter name="title">Fixed Test Cases for query_with_params</parameter>
<parameter name="command">create</parameter>
<parameter name="content">from django.test import TestCase
from unittest.mock import patch, MagicMock
import oracledb
from account_identification.services import query_with_params
import logging

class TestQueryWithParams(TestCase):
    """Test cases for query_with_params function."""

    def setUp(self):
        # Suppress logging during tests
        logging.disable(logging.CRITICAL)
        
        # Setup mock data
        self.mock_data = {
            "ACCT_NUM": "12345",
            "ACCT_NAME": "Doe, John",
            "PRIMARY_NUMBER": "5551234567",
            "EMAIL_ADDR": "john.doe@example.com",
            "CITY_NM_BLR": "Springfield",
            "STATE_NM_BLR": "IL",
            "PSTL_CD_TXT_BLR": "62701",
            "BLR_ADDR1_LINE": "123 Main St",
            "BLR_ADDR2_LINE": None,  # Testing null replacement
            "ACCOUNTSTATUS": "Active",
            "ACCT_TYPE_CD": "RES",
            "SRC_SYS_CD": "BHN",
            "SPC_DIV_ID": "DIV123",
            "UCAN": "UCAN123"
        }

    def tearDown(self):
        # Re-enable logging after tests
        logging.disable(logging.NOTSET)

    def setup_cursor_mock(self, mock_cursor, data=None):
        """Helper to setup cursor mock with data"""
        if data is None:
            data = self.mock_data
        
        # Setup cursor description (column names)
        mock_cursor.description = [(k, None, None, None, None, None, None) for k in data.keys()]
        
        # Convert dictionary to list of tuples for row data
        mock_cursor.fetchall.return_value = [(
            data["ACCT_NUM"],
            data["ACCT_NAME"],
            data["PRIMARY_NUMBER"],
            data["EMAIL_ADDR"],
            data["CITY_NM_BLR"],
            data["STATE_NM_BLR"],
            data["PSTL_CD_TXT_BLR"],
            data["BLR_ADDR1_LINE"],
            data["BLR_ADDR2_LINE"],
            data["ACCOUNTSTATUS"],
            data["ACCT_TYPE_CD"],
            data["SRC_SYS_CD"],
            data["SPC_DIV_ID"],
            data["UCAN"]
        )]
        return mock_cursor

    @patch('account_identification.services.connect_to_oracle')
    def test_query_with_params_success(self, mock_connect):
        """Test successful query execution with parameters."""
        # Setup mocks
        mock_cursor = MagicMock()
        self.setup_cursor_mock(mock_cursor)
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        sql = "SELECT * FROM test_table WHERE id = :id"
        params = {"id": 1}
        result = query_with_params(sql, params)

        # Verify results
        print(f"Result length: {len(result)}")  # Debug print
        print(f"Raw cursor data: {mock_cursor.fetchall.return_value}")  # Debug print
        
        self.assertEqual(len(result), 1)
        record = result[0]
        self.assertEqual(record.account_number, "12345")
        self.assertEqual(record._address_line_2, "")  # Null was replaced
        mock_cursor.execute.assert_called_once_with(sql, params)
        mock_cursor.close.assert_called_once()

    @patch('account_identification.services.connect_to_oracle')
    def test_query_with_params_no_params(self, mock_connect):
        """Test query execution without parameters."""
        # Setup mocks
        mock_cursor = MagicMock()
        self.setup_cursor_mock(mock_cursor)
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        result = query_with_params("SELECT * FROM test_table")

        # Verify results
        self.assertEqual(len(result), 1)
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table", {})
        mock_cursor.close.assert_called_once()

    @patch('account_identification.services.connect_to_oracle')
    def test_query_with_params_empty_result(self, mock_connect):
        """Test query returning no results."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_cursor.description = [(k, None, None, None, None, None, None) for k in self.mock_data.keys()]
        mock_cursor.fetchall.return_value = []  # No results
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        result = query_with_params("SELECT * FROM test_table")

        # Verify results
        self.assertEqual(len(result), 0)
        mock_cursor.close.assert_called_once()

    @patch('account_identification.services.connect_to_oracle')
    def test_query_with_params_db_error(self, mock_connect):
        """Test handling of database errors."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = oracledb.Error("Test DB Error")
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query and verify error handling
        with self.assertRaises(oracledb.Error):
            query_with_params("SELECT * FROM test_table")

        # Verify cursor was closed
        mock_cursor.close.assert_called_once()

    @patch('account_identification.services.connect_to_oracle')
    def test_query_with_params_null_values(self, mock_connect):
        """Test handling of null values in result set."""
        # Setup data with multiple null values
        data_with_nulls = self.mock_data.copy()
        data_with_nulls.update({
            "EMAIL_ADDR": None,
            "CITY_NM_BLR": None,
            "BLR_ADDR2_LINE": None
        })

        # Setup mocks
        mock_cursor = MagicMock()
        self.setup_cursor_mock(mock_cursor, data_with_nulls)
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        result = query_with_params("SELECT * FROM test_table")

        # Verify results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].email_address, "")  # Null was replaced
        self.assertEqual(result[0].city, "")  # Null was replaced
        self.assertEqual(result[0]._address_line_2, "")  # Null was replaced
        mock_cursor.close.assert_called_once()</parameter>
<parameter name="language">python</parameter>
</invoke>
</function_calls>

Key changes made:

1. Updated the setup_cursor_mock method to properly simulate Oracle cursor:
   - Added proper cursor.description format (7 elements per column)
   - Correctly formatted the fetchall return value as a list of tuples

2. Changed the mock patches to target 'account_identification.services.connect_to_oracle' directly

3. Added debug print statements in the test_query_with_params_success method to help diagnose any remaining issues

4. Properly structured the mock data to match the exact format expected by the OracleDESRecord conversion

The main issues fixed:
1. Cursor description format was incorrect
2. Mock data structure wasn't matching what the actual cursor would return
3. Mock patch target was wrong

Would you like me to explain any part in more detail or help debug any remaining issues?
