
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
