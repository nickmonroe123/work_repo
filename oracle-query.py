from unittest.mock import Mock, patch, call
import requests
from django.test import TestCase
from parameterized import parameterized
from jira_integration.services import JiraClient, get_jira_updated_issues
from jira_integration import constants

class JiraServiceTestCase(TestCase):
    """Combined test cases for Jira services"""

    def setUp(self):
        """Set up common test data"""
        self.test_jql = "project = TEST"
        self.test_fields = "summary,status"
        self.test_type = "epic"
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
        self.base_params = {
            'jql': self.test_jql,
            'fields': self.test_fields,
            'maxResults': constants.MAX_JQL_RESULTS,
            'startAt': 0
        }

    def create_http_error(self, status_code):
        """Helper method to create HTTPError with specific status code"""
        response = Mock()
        response.status_code = status_code
        error = requests.exceptions.HTTPError()
        error.response = response
        error.__str__ = Mock(return_value=str(status_code))
        return error

    @patch('jira_integration.services.JiraSession')
    def test_search_issues_success(self, mock_session_class):
        """Test successful Jira API search"""
        # Arrange
        mock_session = Mock()
        mock_session.get.return_value = Mock(json=lambda: self.jql_results)
        mock_session_class.return_value = mock_session
        client = JiraClient()

        # Act
        result = client.search_issues(self.test_jql, self.test_fields)

        # Assert
        self.assertEqual(result, self.jql_results)
        mock_session.get.assert_called_once_with('/rest/api/2/search', params=self.base_params)

    @patch('jira_integration.services.JiraSession')
    def test_search_issues_api_error(self, mock_session_class):
        """Test Jira API search error handling"""
        # Arrange
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.RequestException("API Error")
        mock_session_class.return_value = mock_session
        client = JiraClient()

        # Act & Assert
        with self.assertRaises(requests.exceptions.RequestException):
            client.search_issues(self.test_jql, self.test_fields)

    @parameterized.expand([
        (401, "Authentication failed. Please check your access token."),
        (403, "Permission denied. Please check your access permissions."),
        (500, "An unexpected error occurred when getting jira updated issues.")
    ])
    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_http_errors(
        self, status_code, expected_message, mock_logger, mock_client_class
    ):
        """Test handling of different HTTP error codes"""
        # Arrange
        mock_client = Mock()
        http_error = self.create_http_error(status_code)
        mock_client.search_issues.side_effect = http_error
        mock_client_class.return_value = mock_client

        # Act & Assert
        with self.assertRaises(requests.exceptions.HTTPError):
            get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

        # Verify error logging
        mock_logger.error.assert_has_calls([
            call(f"Error occurred: {http_error}"),
            call(expected_message)
        ])

    @patch('jira_integration.services.create_or_update_records')
    @patch('jira_integration.services.JiraClient')
    @patch('jira_integration.services.logger')
    def test_get_jira_updated_issues_success_and_create_error(
        self, mock_logger, mock_client_class, mock_create_or_update
    ):
        """Test successful API call and creation error handling"""
        # Arrange
        mock_client = Mock()
        mock_client.search_issues.return_value = self.jql_results
        mock_client_class.return_value = mock_client

        # Test successful case
        get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)
        mock_create_or_update.assert_called_once_with(self.jql_results, self.test_type)
        mock_logger.error.assert_not_called()

        # Test creation error
        mock_create_or_update.reset_mock()
        mock_create_or_update.side_effect = Exception("Database error")

        with self.assertRaises(Exception):
            get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)
        
        mock_create_or_update.assert_called_once_with(self.jql_results, self.test_type)
