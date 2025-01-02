# test_parsers.py

class StoryParserTestCase(BaseParserTestCase):
    """Test cases for StoryParser class"""

    def setUp(self):
        super().setUp()
        self.base_fields['fields'].update({
            'issuetype': {'name': 'Story'},
            constants.EPIC_LINK: 'EPIC-123'
        })
        self.parser = StoryParser(self.base_fields)

    @patch('jira_integration.models.Epic.objects.get')
    def test_create_or_update_story_with_existing_epic(self, mock_epic_get):
        """Test creating story with existing epic"""
        mock_epic = Mock()
        mock_epic_get.return_value = mock_epic
        
        story_data = self.parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            self.parser.create_or_update(story_data)
            
            expected_defaults = story_data.copy()
            epic_key = expected_defaults.pop('parent')
            
            mock_epic_get.assert_called_once_with(id=epic_key)
            mock_create.assert_called_once_with(
                id=story_data['id'],
                defaults={**expected_defaults, 'parent': mock_epic}
            )

    @patch('jira_integration.models.Epic.objects.get')
    def test_create_or_update_story_with_missing_epic(self, mock_epic_get):
        """Test creating story with non-existent epic"""
        mock_epic_get.side_effect = Epic.DoesNotExist()
        
        story_data = self.parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            with patch('builtins.print') as mock_print:
                self.parser.create_or_update(story_data)
                
                mock_print.assert_called_once_with(
                    f"Warning: Parent Epic EPIC-123 not found for Story {story_data['id']}"
                )
                
                # Verify create called with correct data
                mock_create.assert_called_once_with(
                    id=story_data['id'],
                    defaults=story_data
                )


class TaskParserTestCase(BaseParserTestCase):
    """Test cases for TaskParser class"""

    def setUp(self):
        super().setUp()
        self.base_fields['key'] = 'TEST-123'
        self.base_fields['fields'].update({
            'issuetype': {'name': 'Access Ticket'},
            constants.ASSIGNED_GROUP: {'value': 'IT'},
            constants.CLOSE_CODE: {'value': 'COMPLETED'},
            'issuelinks': [{
                'type': {'inward': 'is child task of'},
                'inwardIssue': {
                    'key': 'STORY-123',
                    'fields': {'project': {'key': 'TEST'}}
                }
            }]
        })
        self.parser = TaskParser(self.base_fields)

    def test_get_parent_with_single_link(self):
        """Test _get_parent with single valid parent link"""
        self.base_fields['key'] = 'TEST-123'  # Ensure key matches project
        result = self.parser._get_parent()
        self.assertEqual(result, 'STORY-123')

    def test_get_parent_with_multiple_links(self):
        """Test _get_parent with multiple parent links"""
        self.base_fields['key'] = 'TEST-123'
        self.base_fields['fields']['issuelinks'] = [
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {
                    'key': 'STORY-123',
                    'fields': {'project': {'key': 'TEST'}}
                }
            },
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {
                    'key': 'STORY-124',
                    'fields': {'project': {'key': 'TEST'}}
                }
            }
        ]
        
        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()
            
            with self.assertRaises(ValueError) as context:
                self.parser._get_parent()
            
            self.assertEqual(
                str(context.exception),
                "Tasks cannot have multiple parents in the same project"
            )

    def test_parse_task_full_data(self):
        """Test parsing task with all fields"""
        self.base_fields['key'] = 'TEST-123'
        result = self.parser.parse()
        
        self.assertEqual(result['issue_type'], 'ACCESS_TICKET')
        self.assertEqual(result['business_unit'], 'IT')
        self.assertEqual(result['close_code'], 'COMPLETED')
        self.assertEqual(result['parent_key'], 'STORY-123')

    @patch('jira_integration.models.Story.objects.get')
    def test_create_or_update_task_with_existing_parent(self, mock_story_get):
        """Test creating task with existing parent story"""
        mock_story = Mock()
        mock_story_get.return_value = mock_story
        
        self.base_fields['key'] = 'TEST-123'
        task_data = self.parser.parse()
        
        with patch('jira_integration.models.Task.objects.update_or_create') as mock_create:
            self.parser.create_or_update(task_data)
            
            expected_defaults = task_data.copy()
            parent_key = expected_defaults.pop('parent_key')
            
            mock_story_get.assert_called_once_with(id=parent_key)
            mock_create.assert_called_once_with(
                id=task_data['id'],
                defaults={**expected_defaults, 'parent': mock_story}
            )

    @patch('jira_integration.models.Story.objects.get')
    def test_create_or_update_task_with_missing_parent(self, mock_story_get):
        """Test creating task with non-existent parent story"""
        mock_story_get.side_effect = Story.DoesNotExist()
        
        self.base_fields['key'] = 'TEST-123'
        task_data = self.parser.parse()
        
        with patch('jira_integration.models.Task.objects.update_or_create') as mock_create:
            with patch('builtins.print') as mock_print:
                self.parser.create_or_update(task_data)
                
                mock_print.assert_called_once_with(
                    f"Warning: Parent Issue STORY-123 not found for Task {task_data['id']}"
                )
                
                # Verify create called with correct data
                expected_defaults = task_data.copy()
                expected_defaults.pop('parent_key')
                mock_create.assert_called_once_with(
                    id=task_data['id'],
                    defaults=expected_defaults
                )
