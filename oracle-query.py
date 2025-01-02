# tests/test_services.py
from django.test import TestCase
from unittest.mock import Mock, patch, call
import requests
from jira_integration.services import get_jira_updated_issues, JiraClient

class GetJiraUpdatedIssuesTestCase(TestCase):
    """Test cases for get_jira_updated_issues function"""
    
    def setUp(self):
        """Set up test data and mocks"""
        self.test_jql = "project = TEST"
        self.test_fields = "summary,status"
        self.test_type = "epic"
        
        # Sample test data
        self.jql_results = {
            "issues": [
                {
                    "key": "TEST-1",
                    "fields": {
                        "summary": "Test Issue",
                        "status": {"name": "Open"}
                    }
                }
            ]
        }

    def create_http_error(self, status_code):
        """Helper method to create HTTPError with specific status code"""
        response = Mock()
        response.status_code = status_code
        error = requests.exceptions.HTTPError()
        error.response = response
        # Set the string representation of the error to include the status code
        error.__str__ = Mock(return_value=str(status_code))
        return error

    @patch('jira_integration.services.create_or_update_records')
    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_success(
        self, mock_logger, mock_client_class, mock_create_or_update
    ):
        """Test successful retrieval and processing of Jira issues"""
        # Arrange
        mock_client = Mock()
        mock_client.search_issues.return_value = self.jql_results
        mock_client_class.return_value = mock_client

        # Act
        get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

        # Assert
        mock_client.search_issues.assert_called_once_with(
            self.test_jql, self.test_fields
        )
        mock_create_or_update.assert_called_once_with(
            self.jql_results, self.test_type
        )
        # Verify no error logging occurred
        mock_logger.error.assert_not_called()

    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_401_error(
        self, mock_logger, mock_client_class
    ):
        """Test handling of 401 authentication error"""
        # Arrange
        mock_client = Mock()
        http_error = self.create_http_error(401)
        mock_client.search_issues.side_effect = http_error
        mock_client_class.return_value = mock_client

        # Act & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

        # Verify error logging
        expected_calls = [
            call(f"Error occurred: {http_error}"),
            call("Authentication failed. Please check your access token.")
        ]
        mock_logger.error.assert_has_calls(expected_calls, any_order=False)

    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_403_error(
        self, mock_logger, mock_client_class
    ):
        """Test handling of 403 permission error"""
        # Arrange
        mock_client = Mock()
        http_error = self.create_http_error(403)
        mock_client.search_issues.side_effect = http_error
        mock_client_class.return_value = mock_client

        # Act & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

        # Verify error logging
        expected_calls = [
            call(f"Error occurred: {http_error}"),
            call("Permission denied. Please check your access permissions.")
        ]
        mock_logger.error.assert_has_calls(expected_calls, any_order=False)

    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_other_http_error(
        self, mock_logger, mock_client_class
    ):
        """Test handling of other HTTP errors"""
        # Arrange
        mock_client = Mock()
        http_error = self.create_http_error(500)
        mock_client.search_issues.side_effect = http_error
        mock_client_class.return_value = mock_client

        # Act & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

        # Verify error logging
        expected_calls = [
            call(f"Error occurred: {http_error}"),
            call("An unexpected error occurred when getting jira updated issues.")
        ]
        mock_logger.error.assert_has_calls(expected_calls, any_order=False)

    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_create_error(
        self, mock_logger, mock_client_class
    ):
        """Test handling of errors during record creation"""
        # Arrange
        mock_client = Mock()
        mock_client.search_issues.return_value = self.jql_results
        mock_client_class.return_value = mock_client

        # Patch create_or_update_records to raise an exception
        with patch('jira_integration.services.create_or_update_records') as mock_create:
            mock_create.side_effect = Exception("Database error")

            # Act & Assert
            with self.assertRaises(Exception):
                get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

            # Verify the function tried to create records
            mock_create.assert_called_once_with(self.jql_results, self.test_type)

class JiraClientTestCase(TestCase):
    """Test cases for JiraClient class"""

    def setUp(self):
        self.client = JiraClient()
        self.test_jql = "project = TEST"
        self.test_fields = "summary,status"

    @patch('jira_integration.services.JiraSession')
    def test_search_issues_success(self, mock_session_class):
        """Test successful search_issues call"""
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"issues": []}
        mock_session = Mock()
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Act
        result = self.client.search_issues(self.test_jql, self.test_fields)

        # Assert
        self.assertEqual(result, {"issues": []})
        mock_session.get.assert_called_once()
        expected_params = {
            'jql': self.test_jql,
            'fields': self.test_fields,
            'maxResults': 50,  # Assuming this is your constant value
            'startAt': 0
        }
        mock_session.get.assert_called_with(
            '/rest/api/2/search',
            params=expected_params
        )

    @patch('jira_integration.services.JiraSession')
    def test_search_issues_http_error(self, mock_session_class):
        """Test handling of HTTP errors in search_issues"""
        # Arrange
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.HTTPError("API Error")
        mock_session_class.return_value = mock_session

        # Act & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            self.client.search_issues(self.test_jql, self.test_fields)
