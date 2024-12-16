class TestIdentifyAccountsView(APITestCase):
    """API Tests for IdentifyAccountsView."""

    def setUp(self):
        super().setUp()
        user = get_user_model()._default_manager.create_user(username='test_user')
        self.client.force_authenticate(user=user)

        self.url = '/account_identification/api/'
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
                    "telephoneNumber": "5551234567",
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
                    "telephoneNumber": "5551234567",
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

    def mock_spectrum_api_call(self, url, **kwargs):
        """Mock response for Spectrum Core API calls"""
        mock_response = MagicMock()
        if 'billing' in url:
            mock_response.json.return_value = self.mock_billing_response
        else:
            mock_response.json.return_value = self.mock_spectrum_response
        mock_response.raise_for_status.return_value = None
        return mock_response

    @patch('requests.request')
    @patch('oracledb.connect')
    @patch('account_identification.services.query_with_params')
    def test_post_success(self, mock_query, mock_connect, mock_request):
        """Test successful POST request with full process mocking."""
        # Setup database mocks
        self.setup_db_mocks(mock_connect)
        mock_query.return_value = [self.mock_oracle_record]

        # Setup API call mocks
        mock_request.side_effect = self.mock_spectrum_api_call

        # Make the request
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        
        # Verify response structure
        results = response.json()
        self.assertTrue(isinstance(results, list))
        self.assertTrue(len(results) > 0)
        
        # Verify each result has required fields
        for result in results:
            self.assertIn('match_score', result)
            self.assertIn('account_type', result)
            self.assertIn('status', result)
            self.assertIn('source', result)
            self.assertIn('ucan', result)
            self.assertIn('billing_account_number', result)
            self.assertIn('spectrum_core_account', result)
            self.assertIn('spectrum_core_division', result)

        # Verify API calls were made
        self.assertTrue(mock_request.called)
        # Verify DB queries were made
        self.assertTrue(mock_query.called)

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
        mock_request.return_value = mock_response

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])</parameter>
<parameter name="language">python</parameter>
</invoke>
