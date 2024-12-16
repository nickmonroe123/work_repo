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

    def setup_db_mocks(self, mock_connect):
        """Helper method to setup database connection mocks"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [tuple(self.mock_record.values())]
        mock_cursor.description = [(k,) for k in self.mock_record.keys()]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_all_valid(self, mock_connect, mock_query):
        """Test oracle_des_process with all valid fields"""
        self.account_process.oracle_des_list = []
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]

        self.account_process.oracle_des_process()

        self.assertEqual(mock_query.call_count, 4)  # All four searches executed
        self.assertEqual(len(self.account_process.oracle_des_list), 4)


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

Can you help me write a test case that goes against the query_with_params function using django test suite and not pytest. For this specific case
i want it to only run the code that doesnt require connection. i want 100% coverage of the file, so if some lines need ignored due to connecting to an external
db then can you make them unneccessary, pragma, etc? Otherwise i want to mimic everything except basically the connect_to_oracle and maybe connection.cursor pieces!
