# Add these test methods to your TaskParserTestCase class

def test_get_parent_existing_task_with_parent(self):
    """Test _get_parent when task exists and has a parent"""
    # Setup task with no issue links
    self.base_fields['fields']['issuelinks'] = []
    
    # Mock existing task with parent
    mock_parent = Mock()
    mock_parent.pk = 'STORY-999'
    mock_task = Mock()
    mock_task.parent = mock_parent
    
    with patch('jira_integration.models.Story.objects.get') as mock_get:
        mock_get.return_value = mock_task
        
        # Act
        result = self.parser._get_parent()
        
        # Assert
        self.assertEqual(result, 'STORY-999')
        mock_get.assert_called_once_with(id=self.base_fields['key'])

def test_get_parent_existing_task_no_parent_raises_error(self):
    """Test _get_parent when task exists but has no parent"""
    # Setup task with no issue links
    self.base_fields['fields']['issuelinks'] = []
    
    # Mock existing task without parent
    mock_task = Mock()
    mock_task.parent = None
    
    with patch('jira_integration.models.Story.objects.get') as mock_get:
        mock_get.return_value = mock_task
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.parser._get_parent()
        
        self.assertEqual(str(context.exception), "Tasks must have parents")
        mock_get.assert_called_once_with(id=self.base_fields['key'])

def test_get_parent_multiple_links_existing_task_no_parent(self):
    """Test _get_parent with multiple links and existing task without parent"""
    # Setup multiple issue links
    self.base_fields['fields']['issuelinks'] = [
        {
            'type': {'inward': 'is child task of'},
            'inwardIssue': {
                'key': 'TEST-124',
                'fields': {'project': {'key': 'TEST'}}
            }
        },
        {
            'type': {'inward': 'is child task of'},
            'inwardIssue': {
                'key': 'TEST-125',
                'fields': {'project': {'key': 'TEST'}}
            }
        }
    ]
    
    # Mock existing task without parent
    mock_task = Mock()
    mock_task.parent = None
    
    with patch('jira_integration.models.Story.objects.get') as mock_get:
        mock_get.return_value = mock_task
        
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.parser._get_parent()
        
        self.assertEqual(
            str(context.exception),
            "Tasks cannot have multiple parents in the same project"
        )
        mock_get.assert_called_once_with(id=self.base_fields['key'])

def test_get_parent_new_task_no_links(self):
    """Test _get_parent for new task with no links"""
    # Setup task with no issue links
    self.base_fields['fields']['issuelinks'] = []
    
    with patch('jira_integration.models.Story.objects.get') as mock_get:
        mock_get.side_effect = Story.DoesNotExist()
        
        # Act
        result = self.parser._get_parent()
        
        # Assert
        self.assertIsNone(result)
        mock_get.assert_called_once_with(id=self.base_fields['key'])
