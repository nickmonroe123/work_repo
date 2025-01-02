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
    """Test cases for Jira update tasks"""

    def setUp(self):
        """Set up common test dependencies"""
        # Create a mock task instance since tasks are bound
        self.mock_task = Mock()
        self.mock_task.request.id = 'test-task-id'

        # Create mock async result for task execution checks
        self.mock_async_result = Mock()
        self.mock_async_result.successful.return_value = True

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_epic_updates_success(self, mock_services, mock_logger):
        """Test successful epic updates fetch"""
        # Act
        result = fetch_jira_epic_updates(self.mock_task)

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once_with(
            jql=constants.EPIC_JQL,
            fields=constants.EPIC_FIELDS,
            jira_type='epic'
        )
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
            fetch_jira_epic_updates(self.mock_task)
        
        self.assertIn("Epic update failed", str(context.exception))
        self.assertIn("API Error", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Error in fetch_jira_epic_updates: API Error"
        )

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_story_updates_success(self, mock_services, mock_logger):
        """Test successful story updates fetch"""
        # Act
        result = fetch_jira_story_updates(self.mock_task)

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once_with(
            jql=constants.STORY_JQL,
            fields=constants.STORY_FIELDS,
            jira_type='story'
        )
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
            fetch_jira_story_updates(self.mock_task)
        
        self.assertIn("Story update failed", str(context.exception))
        self.assertIn("API Error", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Error in fetch_jira_story_updates: API Error"
        )

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_task_updates_success(self, mock_services, mock_logger):
        """Test successful task updates fetch"""
        # Act
        result = fetch_jira_task_updates(self.mock_task)

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once_with(
            jql=constants.TASK_JQL,
            fields=constants.TASK_FIELDS,
            jira_type='task'
        )
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
            fetch_jira_task_updates(self.mock_task)
        
        self.assertIn("Task update failed", str(context.exception))
        self.assertIn("API Error", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Error in fetch_jira_task_updates: API Error"
        )

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
        result = process_jira_updates_and_changes(self.mock_task)

        # Assert
        self.assertTrue(result)
        
        # Verify sequential execution
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()
        mock_task.apply.assert_called_once()
        
        # Verify completion logging
        mock_logger.info.assert_has_calls([
            call("Starting Jira updates process"),
            call("All Jira update processes completed successfully")
        ])

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
            process_jira_updates_and_changes(self.mock_task)
        
        self.assertIn("Epic update process failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Jira update process failed: Epic update process failed"
        )

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
            process_jira_updates_and_changes(self.mock_task)
        
        # Verify error handling and logging
        self.assertIn("Story update process failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Jira update process failed: Story update process failed"
        )
        
        # Verify execution order
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_task_failure(
        self, mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test process failure when task update fails"""
        # Arrange
        mock_epic.apply.return_value = self.mock_async_result
        mock_story.apply.return_value = self.mock_async_result
        failed_result = Mock()
        failed_result.successful.return_value = False
        mock_task.apply.return_value = failed_result

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            process_jira_updates_and_changes(self.mock_task)
        
        # Verify error handling and logging
        self.assertIn("Task update process failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Jira update process failed: Task update process failed"
        )
        
        # Verify execution order
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()
        mock_task.apply.assert_called_once()

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    def test_process_jira_updates_unexpected_error(self, mock_epic, mock_logger):
        """Test handling of unexpected errors in the process"""
        # Arrange
        mock_epic.apply.side_effect = Exception("Unexpected error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            process_jira_updates_and_changes(self.mock_task)
        
        self.assertIn("Unexpected error", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Unexpected error in Jira update process: Unexpected error"
        )
