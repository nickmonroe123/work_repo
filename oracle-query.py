def test_get_parent_with_multiple_links(self):
    """Test _get_parent with multiple parent links"""
    # Arrange
    self.base_fields['key'] = 'TEST-123'
    self.base_fields['fields']['issuelinks'] = [
        {
            'type': {'inward': 'is child task of'},
            'inwardIssue': {
                'key': 'TEST-1234',
                'fields': {'project': {'key': 'TEST'}}
            }
        },
        {
            'type': {'inward': 'is child task of'},
            'inwardIssue': {
                'key': 'TEST-1235',
                'fields': {'project': {'key': 'TEST'}}
            }
        }
    ]
    
    # Create a mock task that exists but has no parent
    mock_task = Mock()
    mock_task.parent = None
    
    with patch('jira_integration.models.Story.objects.get') as mock_get:
        # First simulate finding the existing task
        mock_get.return_value = mock_task
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.parser._get_parent()
        
        self.assertEqual(
            str(context.exception),
            "Tasks cannot have multiple parents in the same project"
        )
