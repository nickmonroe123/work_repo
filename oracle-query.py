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

        # Setup standard mock response data
        self.mock_record = {
            "ACCT_NUM": "12345",
            "ACCT_NAME": "Doe, John",
            "PRIMARY_NUMBER": "5551234567",
            "EMAIL_ADDR": "john.doe@example.com",
            "CITY_NM_BLR": "Springfield",
            "STATE_NM_BLR": "IL",
            "PSTL_CD_TXT_BLR": "62701",
            "BLR_ADDR1_LINE": "123 Main St",
            "BLR_ADDR2_LINE": "",
            "ACCOUNTSTATUS": "Active",
            "ACCT_TYPE_CD": "RES",
            "SRC_SYS_CD": "BHN",
            "SPC_DIV_ID": "DIV123",
            "UCAN": "UCAN123",
        }

    @patch('oracledb.connect')
    def test_query_with_params_success(self, mock_connect):
        """Test successful query execution with parameters."""
        # Setup cursor mock
        mock_cursor = MagicMock()
        mock_cursor.description = [(k,) for k in self.mock_record.keys()]
        # Set fetchall to return a list of tuples matching the mock_record values
        mock_cursor.fetchall.return_value = [tuple(self.mock_record.values())]
        # Make cursor.__iter__ return the same data as fetchall
        mock_cursor.__iter__.return_value = [tuple(self.mock_record.values())]
        
        # Setup connection mock
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        sql = "SELECT * FROM test_table"
        result = query_with_params(sql)

        # Verify the query was executed
        mock_cursor.execute.assert_called_once_with(sql, {})
        
        # Verify cursor was closed
        mock_cursor.close.assert_called_once()
        
        # Verify results
        self.assertEqual(len(result), 1)
        # Verify the returned object is of type OracleDESRecord
        self.assertIsInstance(result[0], OracleDESRecord)
        # Verify the data matches our mock
        self.assertEqual(result[0].ACCT_NUM, self.mock_record["ACCT_NUM"])
        self.assertEqual(result[0].EMAIL_ADDR, self.mock_record["EMAIL_ADDR"])

    @patch('oracledb.connect')
    def test_query_with_params_empty_result(self, mock_connect):
        """Test query execution with no results."""
        # Setup cursor mock with no results
        mock_cursor = MagicMock()
        mock_cursor.description = [(k,) for k in self.mock_record.keys()]
        mock_cursor.fetchall.return_value = []
        mock_cursor.__iter__.return_value = []
        
        # Setup connection mock
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Execute query
        sql = "SELECT * FROM test_table"
        result = query_with_params(sql)

        # Verify empty result list
        self.assertEqual(len(result), 0)
        
        # Verify cursor was closed
        mock_cursor.close.assert_called_once()

def query_with_params(sql_query: str, params: Dict = None) -> List[OracleDESRecord]:
    """Executes a parameterized query and returns results as OracleDESRecords."""
    cursor = None
    try:
        # Connect
        connection = connect_to_oracle(**constants.DB_CONFIG)
        # Create cursor
        cursor = connection.cursor()

        # Execute query with parameters
        cursor.execute(sql_query, params or {})

        # Get column names
        columns = [col[0] for col in cursor.description]

        # Fetch results and convert to list of dictionaries
        results = []
        for row in cursor:
            results.append(dict(zip(columns, row)))

        no_null = replace_null_with_empty_string(results)
        return [msgspec.convert(item, OracleDESRecord) for item in no_null]

    except oracledb.Error as error:
        logger.info(f"Database error: {error}")
        raise

    finally:
        if cursor:
            cursor.close()
