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
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]

        self.account_process.oracle_des_process()

        self.assertEqual(mock_query.call_count, 4)  # All four searches executed
        self.assertEqual(len(self.account_process.oracle_des_list), 4)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_invalid_phone(self, mock_connect, mock_query):
        """Test oracle_des_process with invalid phone number"""
        self.setup_db_mocks(mock_connect)
        self.account_process.ext_request.phone_number = "555123"  # Invalid length
        
        self.account_process.oracle_des_process()
        
        # Phone search should be skipped, but other searches should run
        self.assertEqual(mock_query.call_count, 3)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_bad_phone(self, mock_connect, mock_query):
        """Test oracle_des_process with blacklisted phone number"""
        self.setup_db_mocks(mock_connect)
        self.account_process.ext_request.phone_number = constants.BAD_NUMBERS[0]
        
        self.account_process.oracle_des_process()
        
        # Phone search should be skipped, but other searches should run
        self.assertEqual(mock_query.call_count, 3)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_missing_street(self, mock_connect, mock_query):
        """Test oracle_des_process with missing street information"""
        self.setup_db_mocks(mock_connect)
        self.account_process.ext_request.street_name = ""
        
        self.account_process.oracle_des_process()
        
        # Address search should be skipped
        self.assertTrue(mock_query.call_count < 4)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_empty_email(self, mock_connect, mock_query):
        """Test oracle_des_process with empty email"""
        self.setup_db_mocks(mock_connect)
        self.account_process.ext_request.email_address = ""
        
        self.account_process.oracle_des_process()
        
        # Email search should be skipped
        self.assertTrue(mock_query.call_count < 4)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_no_name_no_zip(self, mock_connect, mock_query):
        """Test oracle_des_process with no name and no zip"""
        self.setup_db_mocks(mock_connect)
        self.account_process.ext_request.first_name = ""
        self.account_process.ext_request.zipcode5 = ""
        
        self.account_process.oracle_des_process()
        
        # Name/zip search should be skipped
        self.assertTrue(mock_query.call_count < 4)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_database_errors(self, mock_connect, mock_query):
        """Test oracle_des_process handling of database errors"""
        self.setup_db_mocks(mock_connect)
        mock_query.side_effect = oracledb.Error("DB Error")

        # Should not raise exceptions
        self.account_process.oracle_des_process()
        
        self.assertEqual(len(self.account_process.oracle_des_list), 0)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_partial_data(self, mock_connect, mock_query):
        """Test oracle_des_process with only some valid fields"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]

        # Setup request with only phone and email
        self.account_process.ext_request = GeneralRequest(
            phone_number="5551234567",
            email_address="test@example.com"
        )

        self.account_process.oracle_des_process()

        # Only phone and email searches should be executed
        self.assertEqual(mock_query.call_count, 2)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_empty_results(self, mock_connect, mock_query):
        """Test oracle_des_process when searches return empty results"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = []  # Empty results

        self.account_process.ext_request = GeneralRequest(
            phone_number="5551234567"  # Only valid phone number
        )
        
        self.account_process.oracle_des_process()
        
        self.assertEqual(len(self.account_process.oracle_des_list), 0)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_only_zip(self, mock_connect, mock_query):
        """Test oracle_des_process with only zipcode"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]

        self.account_process.ext_request = GeneralRequest(
            zipcode5="62701"  # Only zipcode
        )

        self.account_process.oracle_des_process()

        mock_query.assert_called_once()
        self.assertEqual(len(self.account_process.oracle_des_list), 1)

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_oracle_des_process_only_name(self, mock_connect, mock_query):
        """Test oracle_des_process with only first name"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]

        self.account_process.ext_request = GeneralRequest(
            first_name="John"  # Only first name
        )

        self.account_process.oracle_des_process()

        mock_query.assert_called_once()
        self.assertEqual(len(self.account_process.oracle_des_list), 1)

class TestSearchFunctions(TestCase):
    """Test individual search functions used by oracle_des_process"""
    
    def setUp(self):
        self.request = GeneralRequest(
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
    def test_search_with_phone_success(self, mock_connect, mock_query):
        """Test successful phone search"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]
        
        result = search_with_phone(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_search_with_address_success(self, mock_connect, mock_query):
        """Test successful address search"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]
        
        result = search_with_address(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_search_with_email_success(self, mock_connect, mock_query):
        """Test successful email search"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]
        
        result = search_with_email(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_search_with_zip_name_success(self, mock_connect, mock_query):
        """Test successful zip and name search"""
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_record]
        
        result = search_with_zip_name(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    @patch('oracledb.connect')
    def test_search_functions_database_error(self, mock_connect, mock_query):
        """Test database error handling in search functions"""
        self.setup_db_mocks(mock_connect)
        mock_query.side_effect = oracledb.Error("DB Error")

        # Test each search function
        with self.assertRaises(oracledb.Error):
            search_with_phone(self.request)
        
        with self.assertRaises(oracledb.Error):
            search_with_address(self.request)
            
        with self.assertRaises(oracledb.Error):
            search_with_email(self.request)
            
        with self.assertRaises(oracledb.Error):
            search_with_zip_name(self.request)
