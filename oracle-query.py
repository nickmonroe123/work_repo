# tests/test_tasks.py
from django.test import TestCase
from unittest.mock import Mock, patch, call
from celery import states
from jira_integration.tasks import (
    JiraUpdateError,
    fetch_jira_epic_updates,
    fetch_jira_story_updates,
    fetch_jira_task_updates,
    process_jira_updates_and_changes
)

class TasksTestCase(TestCase):
    def setUp(self):
        """Set up common test dependencies"""
        self.mock_async_result = Mock()
        self.mock_async_result.successful.return_value = True

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_epic_updates_success(self, mock_services, mock_logger):
        """Test successful epic updates fetch"""
        # Act
        result = fetch_jira_epic_updates()

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once()
        mock_logger.info.assert_has_calls([
            call("Starting epic updates fetch"),
            call("Completed epic updates fetch")
        ])

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_epic_updates_failure(self, mock_services, mock_logger):
        """Test epic updates fetch failure"""
        # Arrange
        mock_services.get_jira_updated_issues.side_effect = Exception("API Error")

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            fetch_jira_epic_updates()
        
        self.assertIn("Epic update failed", str(context.exception))
        mock_logger.error.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_story_updates_success(self, mock_services, mock_logger):
        """Test successful story updates fetch"""
        # Act
        result = fetch_jira_story_updates()

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once()
        mock_logger.info.assert_has_calls([
            call("Starting story updates fetch"),
            call("Completed story updates fetch")
        ])

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_story_updates_failure(self, mock_services, mock_logger):
        """Test story updates fetch failure"""
        # Arrange
        mock_services.get_jira_updated_issues.side_effect = Exception("API Error")

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            fetch_jira_story_updates()
        
        self.assertIn("Story update failed", str(context.exception))
        mock_logger.error.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_task_updates_success(self, mock_services, mock_logger):
        """Test successful task updates fetch"""
        # Act
        result = fetch_jira_task_updates()

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once()
        mock_logger.info.assert_has_calls([
            call("Starting task updates fetch"),
            call("Completed task updates fetch")
        ])

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_task_updates_failure(self, mock_services, mock_logger):
        """Test task updates fetch failure"""
        # Arrange
        mock_services.get_jira_updated_issues.side_effect = Exception("API Error")

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            fetch_jira_task_updates()
        
        self.assertIn("Task update failed", str(context.exception))
        mock_logger.error.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_success(
        self, mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test successful sequential processing of all updates"""
        # Arrange
        mock_epic.apply.return_value = self.mock_async_result
        mock_story.apply.return_value = self.mock_async_result
        mock_task.apply.return_value = self.mock_async_result

        # Act
        result = process_jira_updates_and_changes()

        # Assert
        self.assertTrue(result)
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()
        mock_task.apply.assert_called_once()
        mock_logger.info.assert_called_with("All Jira update processes completed successfully")

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    def test_process_jira_updates_epic_failure(self, mock_epic, mock_logger):
        """Test process failure when epic update fails"""
        # Arrange
        failed_result = Mock()
        failed_result.successful.return_value = False
        mock_epic.apply.return_value = failed_result

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            process_jira_updates_and_changes()
        
        self.assertIn("Epic update process failed", str(context.exception))
        mock_logger.error.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    def test_process_jira_updates_story_failure(
        self, mock_story, mock_epic, mock_logger
    ):
        """Test process failure when story update fails"""
        # Arrange
        mock_epic.apply.return_value = self.mock_async_result
        failed_result = Mock()
        failed_result.successful.return_value = False
        mock_story.apply.return_value = failed_result

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            process_jira_updates_and_changes()
        
        self.assertIn("Story update process failed", str(context.exception))
        mock_logger.error.assert_called_once()

# tests/test_services.py
from django.test import TestCase
from unittest.mock import Mock, patch
import requests
from jira_integration import services

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

# tests/test_parsers.py
from django.test import TestCase
from jira_integration import parsers
from jira_integration.models import Epic, Story, Task

class ParserTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.epic_data = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Epic",
                "status": {"name": "In Progress"},
                "issuetype": {"name": "Epic"},
                "resolutiondate": None
            }
        }
        
        self.story_data = {
            "key": "PROJ-124",
            "fields": {
                "summary": "Test Story",
                "status": {"name": "In Progress"},
                "issuetype": {"name": "Story"},
                "customfield_10014": "PROJ-123",  # Epic link
                "resolutiondate": None
            }
        }

    def test_epic_parser(self):
        """Test Epic parsing"""
        # Arrange
        parser = parsers.EpicParser(self.epic_data)

        # Act
        result = parser.parse()

        # Assert
        self.assertEqual(result["id"], "PROJ-123")
        self.assertEqual(result["summary"], "Test Epic")
        self.assertEqual(result["status"], "IN_PROGRESS")

    def test_story_parser(self):
        """Test Story parsing"""
        # Arrange
        parser = parsers.StoryParser(self.story_data)

        # Act
        result = parser.parse()

        # Assert
        self.assertEqual(result["id"], "PROJ-124")
        self.assertEqual(result["parent"], "PROJ-123")

    def test_create_or_update_records_epic(self):
        """Test creating/updating epic records"""
        # Arrange
        jira_response = {
            "issues": [self.epic_data]
        }

        # Act
        parsers.create_or_update_records(jira_response, "epic")

        # Assert
        epic = Epic.objects.get(id="PROJ-123")
        self.assertEqual(epic.summary, "Test Epic")
        self.assertEqual(epic.status, "IN_PROGRESS")

    def test_create_or_update_records_invalid_type(self):
        """Test handling invalid record type"""
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            parsers.create_or_update_records({}, "invalid_type")
        self.assertIn("Unknown jira_type", str(context.exception))

# Run tests with coverage:
# python manage.py test --verbosity=2
# For coverage report:
# coverage run manage.py test
# coverage report
# coverage html
