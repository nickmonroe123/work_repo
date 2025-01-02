# test_tasks.py

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
        process_jira_updates_and_changes(self.mock_task)
    
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
