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
            state="IL"
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
            "UCAN": "UCAN123"
        }

        # Setup standard mock response data
        self.mock_record_bad = {
            "ACCT_NUM": "12345",
            "ACCT_NAME": "Doe, John",
            "PRIMARY_NUMBER": "5551234567",
            "EMAIL_ADDR": "john.doe@example.com",
            "CITY_NM_BLR": "Springfield",
            "STATE_NM_BLR": "IL",
            "PSTL_CD_TXT_BLR": "62701",
            "BLR_ADDR1_LINE": "123 Main St",
            "BLR_ADDR2_LINE": None,
            "ACCOUNTSTATUS": "Active",
            "ACCT_TYPE_CD": "RES",
            "SRC_SYS_CD": "BHN",
            "SPC_DIV_ID": "DIV123",
            "UCAN": "UCAN123"
        }

    def setup_db_mocks(self, mock_connect):
        """Helper method to setup database connection mocks"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [tuple(self.mock_record.values())]
        mock_cursor.description = [(k,) for k in self.mock_record.keys()]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

    def setup_cursor_mock(self, mock_cursor, data=None):
        """Helper to setup cursor mock with data"""
        if data is None:
            data = self.mock_record_bad
        mock_cursor.description = [(k,) for k in data.keys()]
        mock_cursor.fetchall.return_value = [tuple(data.values())]
        return mock_cursor

    @patch('oracledb.connect')
    def test_query_with_params_success(self, mock_connect):
        """Test successful query execution with parameters."""
        # Setup mocks
        mock_cursor = MagicMock()
        self.setup_cursor_mock(mock_cursor)
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
    
        # Execute query
        sql = "SELECT * FROM test_table"
        result = query_with_params(sql)
    
        # Verify results
        self.assertEqual(len(result), 1)
        mock_cursor.close.assert_called_once()
def query_with_params(sql_query: str, params: Dict = None) -> List[OracleDESRecord]:
    """Executes a parameterized query and returns results as OracleDESRecords.

    Args:
        connection (cx_Oracle.Connection): Database connection
        sql_query (str): SQL query with bind variables
        params (Dict): Dictionary of parameter names and values

    Returns:
        List[OracleDESRecord]: List of OracleDESRecords containing query results
    """
    try:
        # Connect
        connection = connect_to_oracle(**constants.DB_CONFIG)  # pragma: no cover
        # Create cursor
        cursor = connection.cursor()  # pragma: no cover

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

# In the query_with_params function it isnt getting to the get columns through return [msgspec] lines at al?
