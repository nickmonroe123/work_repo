from django.test import TestCase
from unittest.mock import Mock, patch
from parameterized import parameterized
from django.utils.dateparse import parse_datetime
from jira_integration.parsers import (
    JiraParser, EpicParser, StoryParser, TaskParser,
    create_or_update_records
)
from jira_integration.models import Epic, Story, Task
from jira_integration import constants

class ParserTestCase(TestCase):
    """Test cases for Jira parsers"""

    def setUp(self):
        """Set up common test data"""
        self.base_fields = {
            'key': 'TEST-123',
            'fields': {
                'summary': 'Test Issue',
                'status': {'name': 'In Progress'},
                'issuetype': {'name': 'Epic'},
                'resolutiondate': '2024-01-01T12:00:00.000+0000',
                constants.EPIC_LINK: 'EPIC-123',
                constants.ASSIGNED_GROUP: {'value': 'IT'},
                constants.CLOSE_CODE: {'value': 'COMPLETED'},
                'issuelinks': [{
                    'type': {'inward': 'is child task of'},
                    'inwardIssue': {'key': 'STORY-123'}
                }]
            }
        }

    def test_parse_common_fields_all_fields(self):
        """Test parsing all common fields"""
        parser = JiraParser(self.base_fields)
        result = parser.parse()

        self.assertEqual(result['id'], 'TEST-123')
        self.assertEqual(result['summary'], 'Test Issue')
        self.assertEqual(result['status'], 'IN_PROGRESS')
        self.assertEqual(result['issue_type'], 'EPIC')
        self.assertEqual(
            result['close_date'],
            parse_datetime('2024-01-01T12:00:00.000+0000').date()
        )

    def test_parse_common_fields_no_resolution_date(self):
        """Test parsing without resolution date"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields']['resolutiondate'] = None
        
        parser = JiraParser(data)
        result = parser.parse()
        
        self.assertIsNone(result['close_date'])

    @parameterized.expand([
        ('epic', EpicParser, ['Epic']),
        ('story', StoryParser, ['Story']),
        ('task', TaskParser, [
            'Access Ticket', 'Delete Ticket',
            'Appeal Ticket', 'Change Ticket'
        ])
    ])
    def test_parser_issue_types(self, parser_type, parser_class, expected_types):
        """Test get_issue_type for all parser classes"""
        self.assertEqual(parser_class.get_issue_type(), expected_types)

    @patch('jira_integration.models.Epic.objects')
    def test_epic_create_or_update(self, mock_epic_objects):
        """Test epic creation/update"""
        parser = EpicParser(self.base_fields)
        epic_data = parser.parse()
        parser.create_or_update(epic_data)
        
        mock_epic_objects.update_or_create.assert_called_once_with(
            id=epic_data['id'],
            defaults=epic_data
        )

    def test_story_parse(self):
        """Test story parsing with epic link"""
        parser = StoryParser(self.base_fields)
        result = parser.parse()
        
        self.assertEqual(result['parent'], 'EPIC-123')

    def test_story_parse_no_epic(self):
        """Test story parsing without epic link"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields'].pop(constants.EPIC_LINK)
        
        parser = StoryParser(data)
        result = parser.parse()
        
        self.assertEqual(result['parent'], '')

    @patch('jira_integration.models.Epic.objects.get')
    def test_story_create_or_update_with_epic(self, mock_epic_get):
        """Test story creation with existing epic"""
        mock_epic = Mock()
        mock_epic_get.return_value = mock_epic
        
        parser = StoryParser(self.base_fields)
        story_data = parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            parser.create_or_update(story_data)
            
            mock_epic_get.assert_called_once_with(id='EPIC-123')
            mock_create.assert_called_once()

    @patch('jira_integration.models.Epic.objects.get')
    def test_story_create_or_update_missing_epic(self, mock_epic_get):
        """Test story creation with missing epic"""
        mock_epic_get.side_effect = Epic.DoesNotExist()
        
        parser = StoryParser(self.base_fields)
        story_data = parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            with patch('builtins.print') as mock_print:
                parser.create_or_update(story_data)
                
                mock_print.assert_called_once_with(
                    "Warning: Parent Epic EPIC-123 not found for Story TEST-123"
                )

    def test_task_parse_full(self):
        """Test task parsing with all fields"""
        self.base_fields['key'] = 'TEST-123'
        parser = TaskParser(self.base_fields)
        result = parser.parse()
        
        self.assertEqual(result['business_unit'], 'IT')
        self.assertEqual(result['close_code'], 'COMPLETED')

    def test_task_parse_no_close_code(self):
        """Test task parsing without close code"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields'].pop(constants.CLOSE_CODE)
        
        parser = TaskParser(data)
        result = parser.parse()
        
        self.assertIsNone(result['close_code'])

    def test_task_get_parent_single_link(self):
        """Test task parent with single link"""
        self.base_fields['key'] = 'TEST-123'
        parser = TaskParser(self.base_fields)
        result = parser._get_parent()
        
        self.assertEqual(result, 'STORY-123')

    def test_task_get_parent_multiple_links(self):
        """Test task parent with multiple links"""
        self.base_fields['key'] = 'TEST-123'
        self.base_fields['fields']['issuelinks'] = [
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'STORY-123'}
            },
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'STORY-124'}
            }
        ]
        
        parser = TaskParser(self.base_fields)
        
        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()
            
            with self.assertRaises(ValueError) as context:
                parser._get_parent()
            
            self.assertEqual(
                str(context.exception),
                "Tasks cannot have multiple parents in the same project"
            )

    def test_task_get_parent_existing_with_parent(self):
        """Test task parent for existing task with parent"""
        self.base_fields['fields']['issuelinks'] = []
        parser = TaskParser(self.base_fields)
        
        mock_parent = Mock()
        mock_parent.pk = 'STORY-999'
        mock_task = Mock()
        mock_task.parent = mock_parent
        
        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.return_value = mock_task
            result = parser._get_parent()
            
            self.assertEqual(result, 'STORY-999')

    @patch('jira_integration.models.Story.objects.get')
    def test_task_create_or_update_with_parent(self, mock_story_get):
        """Test task creation with existing parent"""
        mock_story = Mock()
        mock_story_get.return_value = mock_story
        
        parser = TaskParser(self.base_fields)
        task_data = parser.parse()
        
        with patch('jira_integration.models.Task.objects.update_or_create') as mock_create:
            parser.create_or_update(task_data)
            
            mock_story_get.assert_called_once()
            mock_create.assert_called_once()

    @parameterized.expand([
        ('epic', EpicParser, 'Epic'),
        ('story', StoryParser, 'Story'),
        ('task', TaskParser, 'Access Ticket')
    ])
    def test_create_or_update_records_full_flow(self, parser_type, parser_class, issue_type):
        """Test full flow of create_or_update_records"""
        self.base_fields['fields']['issuetype']['name'] = issue_type
        jira_json = {'issues': [self.base_fields]}
        
        with patch.object(parser_class, 'create_or_update') as mock_create:
            create_or_update_records(jira_json, parser_type)
            mock_create.assert_called_once()

    def test_create_or_update_records_unknown_type(self):
        """Test handling of unknown parser type"""
        with self.assertRaises(ValueError) as context:
            create_or_update_records({}, 'unknown')
        self.assertEqual(
            str(context.exception),
            "Unknown jira_type: unknown"
        )
