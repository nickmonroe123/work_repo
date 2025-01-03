from celery import shared_task
from celery.utils.log import get_task_logger
from jira_integration import services
from jira_integration import constants

logger = get_task_logger(__name__)

class JiraUpdateError(Exception):
    """Custom exception for Jira update process failures"""
    pass


@shared_task(bind=True)
def fetch_jira_epic_updates(self):
    """Subtask 1: Fetches updated issues from Jira"""
    try:
        logger.info("Starting epic updates fetch")
        services.get_jira_updated_issues(
            jql=constants.EPIC_JQL,
            fields=constants.EPIC_FIELDS,
            jira_type='epic'
        )
        logger.info("Completed epic updates fetch")
        return True
    except Exception as e:
        logger.error(f"Error in fetch_jira_epic_updates: {str(e)}")
        raise JiraUpdateError(f"Epic update failed: {str(e)}")



@shared_task(bind=True)
def fetch_jira_story_updates(self):
    """Subtask 2: Fetches updated stories from Jira"""
    try:
        logger.info("Starting story updates fetch")
        services.get_jira_updated_issues(
            jql=constants.STORY_JQL,
            fields=constants.STORY_FIELDS,
            jira_type='story'
        )
        logger.info("Completed story updates fetch")
        return True
    except Exception as e:
        logger.error(f"Error in fetch_jira_story_updates: {str(e)}")
        raise JiraUpdateError(f"Story update failed: {str(e)}")


@shared_task(bind=True)
def fetch_jira_task_updates(self):
    """Subtask 3: Fetches updated tasks from Jira"""
    try:
        logger.info("Starting task updates fetch")
        services.get_jira_updated_issues(
            jql=constants.TASK_JQL,
            fields=constants.TASK_FIELDS,
            jira_type='task'
        )
        logger.info("Completed task updates fetch")
        return True
    except Exception as e:
        logger.error(f"Error in fetch_jira_task_updates: {str(e)}")
        raise JiraUpdateError(f"Task update failed: {str(e)}")


@shared_task(bind=True)
def process_jira_updates_and_changes(self):
    """
    Main task that processes Jira updates sequentially.
    If any subtask fails, the entire process will fail.

    Execution order:
    1. Fetch Epics
    2. Fetch Stories
    3. Fetch Tasks
    """
    try:
        logger.info("Starting Jira updates process")

        # Step 1: Fetch Epics
        fetch_jira_epic_updates.apply()

        # Step 2: Fetch Stories
        fetch_jira_story_updates.apply()

        # Step 3: Fetch Tasks
        fetch_jira_task_updates.apply()

        logger.info("All Jira update processes completed successfully")
        return True

    except JiraUpdateError as e:
        logger.error(f"Jira update process failed: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error in Jira update process: {str(e)}")
        raise

class TasksTestCase(TestCase):
    """Test cases for Jira update tasks"""

    def setUp(self):
        """Set up common test dependencies"""
        # Create mock async result for task execution checks
        self.mock_async_result = Mock()
        self.mock_async_result.successful.return_value = True

        # Create mock async result for failed cases
        self.mock_failed_result = Mock()
        self.mock_failed_result.successful.return_value = False
        self.mock_failed_result.status = 'FAILURE'
        self.mock_failed_result.result = JiraUpdateError("Task failed")

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_epic_updates_success(self, mock_services, mock_logger):
        """Test successful epic updates fetch"""
        # Act
        result = fetch_jira_epic_updates.apply().get()

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
            fetch_jira_epic_updates.apply().get()

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
        result = fetch_jira_story_updates.apply().get()

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
            fetch_jira_story_updates.apply().get()

        self.assertIn("Story update failed", str(context.exception))
        mock_logger.error.assert_called_once_with(
            "Error in fetch_jira_story_updates: API Error"
        )

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.services')
    def test_fetch_jira_task_updates_success(self, mock_services, mock_logger):
        """Test successful task updates fetch"""
        # Act
        result = fetch_jira_task_updates.apply().get()

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
            fetch_jira_task_updates.apply().get()

        self.assertIn("Task update failed", str(context.exception))
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
        result = process_jira_updates_and_changes.apply().get()

        # Assert
        self.assertTrue(result)
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_called_once()
        mock_task.apply.assert_called_once()
        mock_logger.info.assert_has_calls([
            call("Starting Jira updates process"),
            call("All Jira update processes completed successfully")
        ])

    @patch('jira_integration.tasks.logger')
    @patch('jira_integration.tasks.fetch_jira_epic_updates')
    @patch('jira_integration.tasks.fetch_jira_story_updates')
    @patch('jira_integration.tasks.fetch_jira_task_updates')
    def test_process_jira_updates_catches_jira_update_error(
            self, mock_task, mock_story, mock_epic, mock_logger
    ):
        """Test that process_jira_updates_and_changes properly catches and handles JiraUpdateError"""
        # Arrange
        jira_error = JiraUpdateError("Custom Jira Error")
        mock_epic.apply.side_effect = jira_error

        # Act & Assert
        with self.assertRaises(JiraUpdateError) as context:
            process_jira_updates_and_changes.apply().get()

        # Verify the error is propagated correctly
        self.assertEqual(str(context.exception), "Custom Jira Error")

        # Verify error logging
        mock_logger.error.assert_called_once_with(
            "Jira update process failed: Custom Jira Error"
        )

        # Verify execution stopped after error
        mock_epic.apply.assert_called_once()
        mock_story.apply.assert_not_called()
        mock_task.apply.assert_not_called()


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


Can you help me keep 100% coverage with these test cases, but maybe parametrize or reduce the number of test cases needed. Is there any way to combine multiple test casesthat are doing similar stuff?
