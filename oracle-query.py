from unittest.mock import Mock, patch, call
import requests
from django.test import TestCase


from jira_integration import parsers
from jira_integration.models import Epic, Story, Task
from jira_integration import services
from jira_integration import constants
from jira_integration.tasks import (
    JiraUpdateError,
    fetch_jira_epic_updates,
    fetch_jira_story_updates,
    fetch_jira_task_updates,
    process_jira_updates_and_changes
)


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
        services.get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

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
            services.get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

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
            services.get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

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
            services.get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

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
                services.get_jira_updated_issues(self.test_jql, self.test_fields, self.test_type)

            # Verify the function tried to create records
            mock_create.assert_called_once_with(self.jql_results, self.test_type)

class JiraClientTestCase(TestCase):
    def setUp(self):
        self.mock_response = Mock()
        self.mock_response.json.return_value = {"issues": []}

    @patch('jira_integration.services.JiraSession')
    def test_search_issues_success(self, mock_session_class):
        """Test successful Jira issue search"""
        # Arrange
        mock_session = Mock()
        mock_session.get.return_value = self.mock_response
        mock_session_class.return_value = mock_session
        client = services.JiraClient()

        # Act
        result = client.search_issues("project = TEST", "summary,status")

        # Assert
        self.assertIn("issues", result)
        mock_session.get.assert_called_once()

    @patch('jira_integration.services.JiraSession')
    def test_search_issues_failure(self, mock_session_class):
        """Test Jira issue search failure"""
        # Arrange
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.RequestException("API Error")
        mock_session_class.return_value = mock_session
        client = services.JiraClient()

        # Act & Assert
        with self.assertRaises(Exception):
            client.search_issues("project = TEST", "summary,status")

"""Services for the Jira app."""
import requests

from jira_integration.session import JiraSession
from jira_integration import constants
from jira_integration.parsers import create_or_update_records
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class JiraClient:
    """Class to abstract common API calls to Jira."""

    def __init__(self, base_url: str = None) -> None:
        # self.session = JiraSession(base_url)
        self.session = JiraSession()


    def search_issues(self, jql: str, fields: str, max_results: int = constants.MAX_JQL_RESULTS, start_at: int = 0):
        """Search for issues using JQL."""
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at,
            'fields': fields
        }
        return self.session.get('/rest/api/2/search', params=params).json()


def get_jira_updated_issues(jql: str, fields: str, jira_type: str):
    # Initialize client
    client = JiraClient()

    try:
        # Retrieve all the epics in the given time range
        jql_results = client.search_issues(jql, fields)
        create_or_update_records(jql_results, jira_type)

    except requests.exceptions.HTTPError as e:
        logger.error(f"Error occurred: {e}")
        if hasattr(e.response, 'status_code') and e.response.status_code == 401:
            logger.error("Authentication failed. Please check your access token.")
        elif hasattr(e.response, 'status_code') and e.response.status_code == 403:
            logger.error("Permission denied. Please check your access permissions.")
        else:
            logger.error("An unexpected error occurred when getting jira updated issues.")
        raise
Here are the services current test cases and current code. Can you do the same thing you just did and try to parameterize/condense down this test cases for me while maintaining 100% coverage?
