from django.test import TestCase
from unittest.mock import Mock, patch, call
from parameterized import parameterized
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
        self.mock_async_result = Mock()
        self.mock_async_result.successful.return_value = True

    @parameterized.expand([
        ('epic', fetch_jira_epic_updates, constants.EPIC_JQL, constants.EPIC_FIELDS),
        ('story', fetch_jira_story_updates, constants.STORY_JQL, constants.STORY_FIELDS),
        ('task', fetch_jira_task_updates, constants.TASK_JQL, constants.TASK_FIELDS),
    ])
    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_updates_success(
        self, task_type, task_func, expected_jql, expected_fields, 
        mock_services, mock_logger
    ):
        """Test successful updates fetch for different types"""
        # Act
        result = task_func.apply().get()

        # Assert
        self.assertTrue(result)
        mock_services.get_jira_updated_issues.assert_called_once_with(
            jql=expected_jql,
            fields=expected_fields,
            jira_type=task_type
        )
        mock_logger.info.assert_has_calls([
            call(f"Starting {task_type} updates fetch"),
            call(f"Completed {task_type} updates fetch")
        ])

    @parameterized.expand([
        ('epic', fetch_jira_epic_updates, 'Epic'),
        ('story', fetch_jira_story_updates, 'Story'),
        ('task', fetch_jira_task_updates, 'Task'),
    ])
    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_updates_failure(
        self, task_type, task_func, error_prefix, mock_services, mock_logger
    ):
        """Test updates fetch failure for different types"""
        # Arrange
        mock_services.get_jira_updated_issues.side_effect = Exception("API Error")

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            task_func.apply().get()

        self.assertIn(f"{error_prefix} update failed", str(context.exception))
        self.assertIn("API Error", str(context.exception))
        mock_logger.error.assert_called_once_with(
            f"Error in fetch_jira_{task_type}_updates: API Error"
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
        for mock in [mock_epic, mock_story, mock_task]:
            mock.apply.return_value = self.mock_async_result

        # Act
        result = process_jira_updates_and_changes.apply().get()

        # Assert
        self.assertTrue(result)
        for mock in [mock_epic, mock_story, mock_task]:
            mock.apply.assert_called_once()
        mock_logger.info.assert_has_calls([
            call("Starting Jira updates process"),
            call("All Jira update processes completed successfully")
        ])

    @parameterized.expand([
        ('JiraUpdateError', JiraUpdateError("Custom Jira Error"), 
         "Jira update process failed: Custom Jira Error"),
        ('Exception', Exception("Unexpected system error"), 
         "Unexpected error in Jira update process: Unexpected system error"),
    ])
    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_error_handling(
        self, error_type, error_instance, expected_log,
        mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test error handling in process_jira_updates_and_changes"""
        # Arrange
        mock_epic.apply.side_effect = error_instance

        # Act & Assert
        with self.assertRaises(error_instance.__class__) as context:
            process_jira_updates_and_changes.apply().get()

        # Verify error handling
        self.assertEqual(str(context.exception), str(error_instance))
        mock_logger.error.assert_called_once_with(expected_log)

        # Verify execution stopped after error
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_not_called()
        mock_task.apply.assert_not_called()
