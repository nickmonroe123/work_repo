from django.test import TestCase
from unittest.mock import patch, MagicMock
import requests
from account_identification.services import AccountProcess
from account_identification import constants

class TestBillingFunctions(TestCase):
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
        
        self.account_process.ext_request = self.mock_request

        # Sample dataset for billing_info_specific
        self.sample_dataset = [
            {
                "accountNumber": "12345",
                "uCAN": "",
                "emailAddress": ""
            },
            {
                "accountNumber": "67890",
                "uCAN": "",
                "emailAddress": ""
            }
        ]

    def test_billing_info_specific_success(self):
        """Test billing info specific with valid account numbers"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "uCAN": "UCAN123",
                    "emailAddress": "test@example.com"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None

        with patch('requests.request', return_value=mock_response):
            result = self.account_process.billing_info_specific(self.sample_dataset)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['uCAN'], 'UCAN123')
            self.assertEqual(result[0]['emailAddress'], 'test@example.com')

    def test_billing_info_specific_empty_account(self):
        """Test billing info specific with empty account number"""
        dataset = [{"accountNumber": "", "uCAN": "", "emailAddress": ""}]
        
        result = self.account_process.billing_info_specific(dataset)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['uCAN'], '')
        self.assertEqual(result[0]['emailAddress'], '')

    def test_billing_info_specific_no_matching_records(self):
        """Test billing info specific when no records are found"""
        # Mock API response with empty list
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": []
            }
        }
        mock_response.raise_for_status.return_value = None

        with patch('requests.request', return_value=mock_response):
            result = self.account_process.billing_info_specific(self.sample_dataset)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['uCAN'], '')
            self.assertEqual(result[0]['emailAddress'], '')

    def test_billing_info_specific_api_error(self):
        """Test billing info specific with API error"""
        with patch('requests.request', side_effect=requests.exceptions.RequestException()):
            result = self.account_process.billing_info_specific(self.sample_dataset)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]['uCAN'], '')
            self.assertEqual(result[0]['emailAddress'], '')

    @patch('requests.request')
    def test_billing_search_valid_data(self, mock_request):
        """Test billing search with valid input data"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "findAccountResponse": {
                "accountList": [{
                    "accountNumber": "12345",
                    "uCAN": "UCAN123",
                    "emailAddress": "test@example.com"
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        self.account_process.billing_search()
        self.assertTrue(len(self.account_process.core_services_list) > 0)
        mock_request.assert_called_once()

    def test_billing_search_missing_name(self):
        """Test billing search with missing name"""
        self.account_process.ext_request.first_name = ""
        self.account_process.billing_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_billing_search_invalid_state(self):
        """Test billing search with invalid state"""
        self.account_process.ext_request.state = "Illinois"  # Not 2 characters
        self.account_process.billing_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_billing_search_invalid_zip(self):
        """Test billing search with invalid zip"""
        self.account_process.ext_request.zipcode5 = "123"  # Not 5 digits
        self.account_process.billing_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    def test_billing_search_empty_required_fields(self):
        """Test billing search with multiple empty required fields"""
        self.account_process.ext_request.last_name = ""
        self.account_process.ext_request.first_name = ""
        self.account_process.billing_search()
        self.assertEqual(len(self.account_process.core_services_list), 0)

    @patch('requests.request')
    def test_billing_search_with_post_processing(self, mock_request):
        """Test billing search with post-processing function"""
        # Mock first API call (billing search)
        first_response = MagicMock()
        first_response.json.return_value = {
            "findAccountResponse": {
                "accountList": [{
                    "accountNumber": "12345",
                    "uCAN": "",
                    "emailAddress": ""
                }]
            }
        }
        # Mock second API call (billing info specific)
        second_response = MagicMock()
        second_response.json.return_value = {
            "getSpcAccountDivisionResponse": {
                "spcAccountDivisionList": [{
                    "uCAN": "UCAN123",
                    "emailAddress": "test@example.com"
                }]
            }
        }

        mock_request.side_effect = [first_response, second_response]

        self.account_process.billing_search()
        self.assertTrue(len(self.account_process.core_services_list) > 0)
        self.assertEqual(mock_request.call_count, 2)  # Should be called twice

    @patch('requests.request')
    def test_billing_search_error_in_post_processing(self, mock_request):
        """Test billing search when post-processing encounters an error"""
        # Mock first API call success but second call fails
        first_response = MagicMock()
        first_response.json.return_value = {
            "findAccountResponse": {
                "accountList": [{
                    "accountNumber": "12345",
                    "uCAN": "",
                    "emailAddress": ""
                }]
            }
        }
        mock_request.side_effect = [
            first_response,  # First call succeeds
            requests.exceptions.RequestException()  # Second call fails
        ]

        self.account_process.billing_search()
        self.assertEqual(len(self.account_process.core_services_list), 1)
        self.assertEqual(mock_request.call_count, 2)

    def test_billing_search_invalid_response_format(self):
        """Test billing search with invalid response format"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "unexpectedKey": {}  # Invalid response format
        }
        mock_response.raise_for_status.return_value = None

        with patch('requests.request', return_value=mock_response):
            self.account_process.billing_search()
            self.assertEqual(len(self.account_process.core_services_list), 0)
