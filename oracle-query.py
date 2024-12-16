class TestIdentifyAccountsView(APITestCase):
    """API Tests for IdentifyAccountsView."""

    def setUp(self):
        super().setUp()
        # Create and authenticate user
        user = get_user_model()._default_manager.create_user(username='test_user')
        self.client.force_authenticate(user=user)
        
        # Get the authentication token from the test client
        auth_header = self.client.handler._get_force_auth_header(user)
        self.auth_headers = {
            'Authorization': auth_header['Authorization'],
            'Content-Type': 'application/json'
        }

        # Base URL - adjust if using a different test server
        self.base_url = 'http://testserver'
        self.url = f'{self.base_url}/account_identification/api/'
        
        self.valid_payload = {
            "name": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "",
                "suffix": "",
                "prefix": ""
            },
            "phone_number": {
                "country_code": "",
                "area_code": "555",
                "exchange": "123",
                "line_number": "4567",
                "extension": "",
                "type_code": ""
            },
            "address": {
                "city": "Springfield",
                "state": "IL",
                "line1": "123 Main St",
                "postal_code": "62701",
                "line2": "",
                "country_code": ""
            },
            "email": "john.doe@example.com"
        }

        # Mock data for spectrum core API responses
        self.mock_spectrum_response = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "accountNumber": "12345",
                    "divisionID": "DIV123",
                    "uCAN": "UCAN123",
                    "firstName": "John",
                    "lastName": "Doe",
                    "emailAddress": "john.doe@example.com",
                    "accountStatus": "Active",
                    "addressLine1": "123 Main St",
                    "addressLine2": "",
                    "city": "Springfield",
                    "state": "IL",
                    "zipCode5": "62701",
                    "primaryPhone": "5551234567",
                    "secondaryPhone": "",
                    "accountType": {
                        "description": "Residential"
                    },
                    "sourceMSO": "SPCS"
                }]
            }
        }

        # Mock data for billing API response
        self.mock_billing_response = {
            "findAccountResponse": {
                "accountList": [{
                    "accountNumber": "67890",
                    "divisionID": "DIV456",
                    "uCAN": "UCAN456",
                    "firstName": "John",
                    "lastName": "Doe",
                    "emailAddress": "john.doe@example.com",
                    "accountStatus": "Active",
                    "addressLine1": "123 Main St",
                    "addressLine2": "",
                    "city": "Springfield",
                    "state": "IL",
                    "zipCode5": "62701",
                    "primaryPhone": "5551234567",
                    "secondaryPhone": "",
                    "accountType": {
                        "description": "Residential"
                    },
                    "sourceMSO": "SPCS"
                }]
            }
        }

        # Mock data for Oracle DB responses
        self.mock_oracle_record = {
            "ACCT_NUM": "99999",
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
            "SPC_DIV_ID": "DIV789",
            "UCAN": "UCAN789"
        }

    def setup_db_mocks(self, mock_connect):
        """Helper method to setup database connection mocks"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [tuple(self.mock_oracle_record.values())]
        mock_cursor.description = [(k,) for k in self.mock_oracle_record.keys()]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        self.mock_oracle_record = msgspec.convert(self.mock_oracle_record, OracleDESRecord)

    def mock_spectrum_api_call(self, method, url, **kwargs):
        """Mock response for Spectrum Core API calls"""
        mock_response = MagicMock()
        if 'findAccount' in url:
            mock_response.json.return_value = self.mock_billing_response
        else:
            mock_response.json.return_value = self.mock_spectrum_response
        mock_response.raise_for_status.return_value = None
        return mock_response

    @patch('requests.request')
    @patch('oracledb.connect')
    @patch('account_identification.services.query_with_params')
    def test_post_no_matches(self, mock_query, mock_connect, mock_request):
        """Test successful POST request but with no matches found."""
        # Setup empty results
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = []

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {"spcAccountDivisionList": []},
            "findAccountResponse": {"accountList": []}
        }
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Use requests.post instead of self.client.post
        response = requests.post(
            self.url,
            json=self.valid_payload,
            headers=self.auth_headers
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
