# tests.py
from django.test import TestCase
from unittest.mock import Mock, patch, call
from celery.exceptions import TaskError
from jira_integration.tasks import (
    JiraUpdateError,
    fetch_jira_epic_updates,
    fetch_jira_story_updates,
    fetch_jira_task_updates,
    process_jira_updates_and_changes
)
from jira_integration import constants

class TasksTestCase(TestCase):
    """Test cases for Jira update tasks"""

    def setUp(self):
        """Set up common test dependencies"""
        # Create mock async result for successful cases
        self.mock_async_result = Mock()
        self.mock_async_result.successful.return_value = True
        
        # Create mock async result for failed cases
        self.mock_failed_result = Mock()
        self.mock_failed_result.successful.return_value = False
        self.mock_failed_result.status = 'FAILURE'
        self.mock_failed_result.result = JiraUpdateError("Task failed")

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_task_updates_raises_error(self, mock_services, mock_logger):
        """Test that task updates properly raises JiraUpdateError"""
        # Arrange
        mock_services.get_jira_updated_issues.side_effect = Exception("Task API Error")

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            fetch_jira_task_updates.apply().get()
        
        self.assertIn("Task update failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Error in fetch_jira_task_updates: Task API Error"
        )

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_task_failure(
        self, mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test process handling when task update fails"""
        # Arrange
        mock_epic.apply.return_value = self.mock_async_result
        mock_story.apply.return_value = self.mock_async_result
        mock_task.apply.return_value = self.mock_failed_result

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            process_jira_updates_and_changes.apply().get()
        
        self.assertIn("Task update process failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Jira update process failed: Task update process failed"
        )
        
        # Verify the execution order
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()
        mock_task.apply.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    def test_process_jira_updates_unexpected_error(self, mock_epic, mock_logger):
        """Test process handling of unexpected errors"""
        # Arrange
        unexpected_error = Exception("Unexpected system error")
        mock_epic.apply.side_effect = unexpected_error

        # Act & Assert
        with self.assertRaises(Exception) as context:
            process_jira_updates_and_changes.apply().get()
        
        self.assertEqual(str(context.exception), "Unexpected system error")
        mock_logger.error.assert_called_once_with(
            "Unexpected error in Jira update process: Unexpected system error"
        )

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_full_failure_path(
        self, mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test the full error path in process_jira_updates_and_changes"""
        # Arrange
        mock_epic.apply.return_value = self.mock_async_result
        mock_story.apply.return_value = self.mock_async_result
        
        # Make task.apply() raise an unexpected error
        mock_task.apply.side_effect = Exception("System crash")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            process_jira_updates_and_changes.apply().get()
        
        # Verify error handling
        self.assertEqual(str(context.exception), "System crash")
        mock_logger.error.assert_called_once_with(
            "Unexpected error in Jira update process: System crash"
        )
        
        # Verify execution order
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()
        mock_task.apply.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_task_exception(
        self, mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test handling of task execution exceptions"""
        # Arrange
        mock_epic.apply.return_value = self.mock_async_result
        mock_story.apply.return_value = self.mock_async_result
        
        # Make task raise JiraUpdateError
        error_result = Mock()
        error_result.successful.return_value = False
        error_result.get.side_effect = JiraUpdateError("Task process error")
        mock_task.apply.return_value = error_result

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            process_jira_updates_and_changes.apply().get()
        
        self.assertIn("Task update process failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Jira update process failed: Task update process failed"
        )
