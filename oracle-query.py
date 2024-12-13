from django.test import TestCase
from unittest.mock import patch, MagicMock
import oracledb
from account_identification.services import (
    AccountProcess,
    search_with_phone,
    search_with_address,
    search_with_email,
    search_with_zip_name
)
from account_identification import constants
from identifiers.structs import GeneralRequest

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

    @patch('account_identification.services.search_with_phone')
    @patch('account_identification.services.search_with_address')
    @patch('account_identification.services.search_with_email')
    @patch('account_identification.services.search_with_zip_name')
    def test_oracle_des_process_all_valid(
        self, mock_zip_name, mock_email, mock_address, mock_phone
    ):
        """Test oracle_des_process with all valid fields"""
        # Setup mock returns
        mock_phone.return_value = [{"phone_record": "data"}]
        mock_address.return_value = [{"address_record": "data"}]
        mock_email.return_value = [{"email_record": "data"}]
        mock_zip_name.return_value = [{"zip_name_record": "data"}]

        self.account_process.oracle_des_process()

        # Verify all search functions were called
        mock_phone.assert_called_once()
        mock_address.assert_called_once()
        mock_email.assert_called_once()
        mock_zip_name.assert_called_once()

        # Verify results were added to oracle_des_list
        self.assertEqual(len(self.account_process.oracle_des_list), 4)

    @patch('account_identification.services.search_with_phone')
    def test_oracle_des_process_invalid_phone(self, mock_phone):
        """Test oracle_des_process with invalid phone number"""
        self.account_process.ext_request.phone_number = "555123"  # Invalid length
        
        self.account_process.oracle_des_process()
        
        mock_phone.assert_not_called()

    @patch('account_identification.services.search_with_phone')
    def test_oracle_des_process_bad_phone(self, mock_phone):
        """Test oracle_des_process with blacklisted phone number"""
        self.account_process.ext_request.phone_number = constants.BAD_NUMBERS[0]
        
        self.account_process.oracle_des_process()
        
        mock_phone.assert_not_called()

    @patch('account_identification.services.search_with_address')
    def test_oracle_des_process_missing_street(self, mock_address):
        """Test oracle_des_process with missing street information"""
        self.account_process.ext_request.street_name = ""
        self.account_process.ext_request.street_number = "123"
        
        self.account_process.oracle_des_process()
        
        mock_address.assert_not_called()

    @patch('account_identification.services.search_with_email')
    def test_oracle_des_process_empty_email(self, mock_email):
        """Test oracle_des_process with empty email"""
        self.account_process.ext_request.email_address = ""
        
        self.account_process.oracle_des_process()
        
        mock_email.assert_not_called()

    @patch('account_identification.services.search_with_zip_name')
    def test_oracle_des_process_no_name_no_zip(self, mock_zip_name):
        """Test oracle_des_process with no name and no zip"""
        self.account_process.ext_request.first_name = ""
        self.account_process.ext_request.zipcode5 = ""
        
        self.account_process.oracle_des_process()
        
        mock_zip_name.assert_not_called()

    @patch('account_identification.services.search_with_phone')
    @patch('account_identification.services.search_with_address')
    @patch('account_identification.services.search_with_email')
    @patch('account_identification.services.search_with_zip_name')
    def test_oracle_des_process_database_errors(
        self, mock_zip_name, mock_email, mock_address, mock_phone
    ):
        """Test oracle_des_process handling of database errors"""
        mock_phone.side_effect = oracledb.Error("DB Error")
        mock_address.side_effect = oracledb.Error("DB Error")
        mock_email.side_effect = oracledb.Error("DB Error")
        mock_zip_name.side_effect = oracledb.Error("DB Error")

        # Should not raise exceptions
        self.account_process.oracle_des_process()

        mock_phone.assert_called_once()
        mock_address.assert_called_once()
        mock_email.assert_called_once()
        mock_zip_name.assert_called_once()
        
        self.assertEqual(len(self.account_process.oracle_des_list), 0)

    @patch('account_identification.services.search_with_phone')
    @patch('account_identification.services.search_with_address')
    @patch('account_identification.services.search_with_email')
    @patch('account_identification.services.search_with_zip_name')
    def test_oracle_des_process_partial_data(
        self, mock_zip_name, mock_email, mock_address, mock_phone
    ):
        """Test oracle_des_process with only some valid fields"""
        # Setup request with only phone and email
        self.account_process.ext_request = GeneralRequest(
            phone_number="5551234567",
            email_address="test@example.com",
            # Other fields empty
        )

        mock_phone.return_value = [{"phone_record": "data"}]
        mock_email.return_value = [{"email_record": "data"}]

        self.account_process.oracle_des_process()

        # Only phone and email searches should be called
        mock_phone.assert_called_once()
        mock_address.assert_not_called()
        mock_email.assert_called_once()
        mock_zip_name.assert_not_called()

        self.assertEqual(len(self.account_process.oracle_des_list), 2)

    @patch('account_identification.services.search_with_phone')
    def test_oracle_des_process_empty_results(self, mock_phone):
        """Test oracle_des_process when searches return empty results"""
        self.account_process.ext_request = GeneralRequest(
            phone_number="5551234567"  # Only valid phone number
        )
        
        mock_phone.return_value = []  # Empty result
        
        self.account_process.oracle_des_process()
        
        mock_phone.assert_called_once()
        self.assertEqual(len(self.account_process.oracle_des_list), 0)

    @patch('account_identification.services.search_with_zip_name')
    def test_oracle_des_process_only_zip(self, mock_zip_name):
        """Test oracle_des_process with only zipcode"""
        self.account_process.ext_request = GeneralRequest(
            zipcode5="62701"  # Only zipcode
        )

        mock_zip_name.return_value = [{"zip_name_record": "data"}]

        self.account_process.oracle_des_process()

        mock_zip_name.assert_called_once()
        self.assertEqual(len(self.account_process.oracle_des_list), 1)

    @patch('account_identification.services.search_with_zip_name')
    def test_oracle_des_process_only_name(self, mock_zip_name):
        """Test oracle_des_process with only first name"""
        self.account_process.ext_request = GeneralRequest(
            first_name="John"  # Only first name
        )

        mock_zip_name.return_value = [{"zip_name_record": "data"}]

        self.account_process.oracle_des_process()

        mock_zip_name.assert_called_once()
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

    @patch('account_identification.services.query_with_params')
    def test_search_with_phone_success(self, mock_query):
        """Test successful phone search"""
        mock_query.return_value = [{"ACCT_NUM": "12345"}]
        
        result = search_with_phone(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    def test_search_with_address_success(self, mock_query):
        """Test successful address search"""
        mock_query.return_value = [{"ACCT_NUM": "12345"}]
        
        result = search_with_address(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    def test_search_with_email_success(self, mock_query):
        """Test successful email search"""
        mock_query.return_value = [{"ACCT_NUM": "12345"}]
        
        result = search_with_email(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    def test_search_with_zip_name_success(self, mock_query):
        """Test successful zip and name search"""
        mock_query.return_value = [{"ACCT_NUM": "12345"}]
        
        result = search_with_zip_name(self.request)
        
        self.assertTrue(len(result) > 0)
        mock_query.assert_called_once()

    @patch('account_identification.services.query_with_params')
    def test_search_functions_database_error(self, mock_query):
        """Test database error handling in search functions"""
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
