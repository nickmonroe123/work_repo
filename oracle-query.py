class TestSpectrumCoreAPI(TestCase):
    def setUp(self):
        self.account_process = AccountProcess()
        # Setup a mock request object
        self.mock_request = MagicMock()
        self.mock_request.first_name = "John"
        self.mock_request.last_name = "Doe"
        self.mock_request.phone_number = "5551234567"
        self.mock_request.email_address = "john.doe@example.com"
        self.mock_request.street_number = "123"
        self.mock_request.street_name = "Main St"
        self.mock_request.city = "Springfield"
        self.mock_request.state = "IL"
        self.mock_request.zipcode5 = "62701"
        self.mock_request.apartment = "4B"
        
        self.account_process.ext_request = self.mock_request

    def test_parse_spectrum_core_api_success(self):
        """Test successful API parsing with valid response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "accountNumber": "12345",
                    "firstName": "John",
                    "lastName": "Doe"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None

        with patch('requests.request', return_value=mock_response):
            result = self.account_process._parse_spectrum_core_api(
                payload={},
                function_url="test_url",
                function_name="test"
            )
            self.assertTrue(len(result) > 0)
            self.assertEqual(len(result), 1)

    def test_parse_spectrum_core_api_empty_response(self):
        """Test API parsing with empty response list"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": []
            }
        }
        mock_response.raise_for_status.return_value = None

        with patch('requests.request', return_value=mock_response):
            result = self.account_process._parse_spectrum_core_api(
                payload={},
                function_url="test_url",
                function_name="test"
            )
            self.assertEqual(len(result), 0)

    def test_parse_spectrum_core_api_invalid_format(self):
        """Test API parsing with invalid response format"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "unexpectedKey": {}
        }
        mock_response.raise_for_status.return_value = None

        with patch('requests.request', return_value=mock_response):
            with self.assertRaises(ValueError):
                self.account_process._parse_spectrum_core_api(
                    payload={},
                    function_url="test_url",
                    function_name="test"
                )

    def test_parse_spectrum_core_api_request_exception(self):
        """Test API parsing with request exception"""
        with patch('requests.request', side_effect=requests.exceptions.RequestException()):
            with self.assertRaises(requests.exceptions.RequestException):
                self.account_process._parse_spectrum_core_api(
                    payload={},
                    function_url="test_url",
                    function_name="test"
                )

    @patch('requests.request')
    def test_phone_search_valid_number(self, mock_request):
        """Test phone search with valid phone number"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "accountNumber": "12345"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        self.account_process.phone_search()
        self.assertTrue(len(self.account_process.core_services_list) > 0)
        mock_request.assert_called_once()

    def test_phone_search_invalid_length(self):
        """Test phone search with invalid phone number length"""
        self.account_process.ext_request.phone_number = "555123"  # Too short
        self.account_process.phone_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_phone_search_bad_number(self):
        """Test phone search with blacklisted phone number"""
        self.account_process.ext_request.phone_number = constants.BAD_NUMBERS[0]
        self.account_process.phone_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    @patch('requests.request')
    def test_name_zip_search_valid(self, mock_request):
        """Test name and zip search with valid data"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "accountNumber": "12345"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        self.account_process.name_zip_search()
        self.assertTrue(len(self.account_process.core_services_list) > 0)
        mock_request.assert_called_once()

    def test_name_zip_search_invalid_zip(self):
        """Test name and zip search with invalid zip code"""
        self.account_process.ext_request.zipcode5 = "123"  # Too short
        self.account_process.name_zip_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_name_zip_search_missing_name(self):
        """Test name and zip search with missing name"""
        self.account_process.ext_request.first_name = ""
        self.account_process.name_zip_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    @patch('requests.request')
    def test_email_search_valid(self, mock_request):
        """Test email search with valid email"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "accountNumber": "12345"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        self.account_process.email_search()
        self.assertTrue(len(self.account_process.core_services_list) > 0)
        mock_request.assert_called_once()

    def test_email_search_empty_email(self):
        """Test email search with empty email"""
        self.account_process.ext_request.email_address = ""
        self.account_process.email_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_clean_address_search_matching_apt(self):
        """Test address cleaning with matching apartment number"""
        test_records = [{
            'addressLine2': '4B',
            'addressLine1': '123 Main St'
        }]
        result = self.account_process.clean_address_search(test_records)
        self.assertEqual(len(result), 1)

    def test_clean_address_search_non_matching_apt(self):
        """Test address cleaning with non-matching apartment number"""
        test_records = [{
            'addressLine2': '5C',
            'addressLine1': '123 Main St'
        }]
        result = self.account_process.clean_address_search(test_records)
        self.assertEqual(len(result), 0)

    def test_clean_address_search_full_address_match(self):
        """Test address cleaning with matching full address"""
        test_records = [{
            'addressLine2': '',
            'addressLine1': '123MainSt4B'
        }]
        result = self.account_process.clean_address_search(test_records)
        self.assertEqual(len(result), 1)

    @patch('requests.request')
    def test_address_search_valid(self, mock_request):
        """Test address search with valid address"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "accountNumber": "12345",
                    "addressLine1": "123 Main St",
                    "addressLine2": "4B"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        self.account_process.address_search()
        self.assertTrue(len(self.account_process.core_services_list) > 0)
        mock_request.assert_called_once()

    def test_address_search_invalid_state(self):
        """Test address search with invalid state length"""
        self.account_process.ext_request.state = "Illinois"  # Not 2 characters
        self.account_process.address_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_address_search_missing_street(self):
        """Test address search with missing street information"""
        self.account_process.ext_request.street_number = ""
        self.account_process.address_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_address_search_invalid_zip(self):
        """Test address search with invalid zip code"""
        self.account_process.ext_request.zipcode5 = "123"  # Not 5 digits
        self.account_process.address_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)
