# test_parsers.py
from django.test import TestCase
from django.utils.dateparse import parse_datetime
from unittest.mock import Mock, patch
from parameterized import parameterized
from jira_integration.parsers import (
    JiraParser, EpicParser, StoryParser, TaskParser,
    create_or_update_records
)
from jira_integration.models import Epic, Story, Task
from jira_integration import constants


class BaseParserTestCase(TestCase):
    """Base test case with common setup for all parser tests"""

    def setUp(self):
        """Set up common test data"""
        self.base_fields = {
            'key': 'TEST-123',
            'fields': {
                'summary': 'Test Issue',
                'status': {'name': 'In Progress'},
                'issuetype': {'name': 'Story'},
                'resolutiondate': '2024-01-01T12:00:00.000+0000',
                constants.EPIC_LINK: 'EPIC-123',
                constants.ASSIGNED_GROUP: {'value': 'IT'},
                constants.CLOSE_CODE: {'value': 'COMPLETED'},
                'issuelinks': [{
                    'type': {'inward': 'is child task of'},
                    'inwardIssue': {
                        'key': 'TEST-1234',
                        'fields': {'project': {'key': 'TEST'}}
                    }
                }]
            }
        }


class ParserTestCase(BaseParserTestCase):
    """Combined test cases for common parser functionality"""

    def test_parse_common_fields_with_resolution_date(self):
        """Test parsing common fields with resolution date"""
        parser = JiraParser(self.base_fields)
        result = parser.parse_common_fields(self.base_fields)

        self.assertEqual(result['id'], 'TEST-123')
        self.assertEqual(result['summary'], 'Test Issue')
        self.assertEqual(result['status'], 'IN_PROGRESS')
        self.assertEqual(result['issue_type'], 'STORY')
        self.assertEqual(
            result['close_date'],
            parse_datetime('2024-01-01T12:00:00.000+0000').date()
        )

    def test_parse_common_fields_without_resolution_date(self):
        """Test parsing common fields without resolution date"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields']['resolutiondate'] = None

        parser = JiraParser(data)
        result = parser.parse_common_fields(data)

        self.assertIsNone(result['close_date'])

    @parameterized.expand([
        ('epic', EpicParser, 'Epic', ['Epic']),
        ('story', StoryParser, 'Story', ['Story']),
        ('task', TaskParser, 'Access Ticket', 
         ['Access Ticket', 'Delete Ticket', 'Appeal Ticket', 'Change Ticket'])
    ])
    def test_parser_types_and_parsing(self, parser_type, parser_class, 
                                    issue_type, expected_types):
        """Test issue types and basic parsing for all parsers"""
        # Test get_issue_type
        self.assertEqual(parser_class.get_issue_type(), expected_types)
        
        # Test basic parsing
        self.base_fields['fields']['issuetype']['name'] = issue_type
        parser = parser_class(self.base_fields)
        result = parser.parse()
        self.assertEqual(result['issue_type'], issue_type.upper().replace(' ', '_'))

    @parameterized.expand([
        ('epic', EpicParser, 'Epic'),
        ('story', StoryParser, 'Story'),
        ('task', TaskParser, 'Access Ticket')
    ])
    def test_create_or_update_records_flow(self, parser_type, parser_class, issue_type):
        """Test the basic create/update flow for each parser type"""
        jira_json = {'issues': [self.base_fields]}
        self.base_fields['fields']['issuetype']['name'] = issue_type

        with patch.object(parser_class, 'create_or_update') as mock_create:
            create_or_update_records(jira_json, parser_type)
            mock_create.assert_called_once()

    def test_create_or_update_records_unknown_type(self):
        """Test handling of unknown jira_type"""
        with self.assertRaises(ValueError) as context:
            create_or_update_records({}, 'unknown')
        self.assertEqual(str(context.exception), "Unknown jira_type: unknown")

    def test_create_or_update_records_empty_issues(self):
        """Test handling empty issues list"""
        create_or_update_records({'issues': []}, 'epic')

    def test_create_or_update_records_wrong_type(self):
        """Test handling issues of wrong type"""
        self.base_fields['fields']['issuetype']['name'] = 'Wrong Type'
        create_or_update_records({'issues': [self.base_fields]}, 'epic')


class StoryParserTestCase(BaseParserTestCase):
    """Test cases specific to Story parsing"""

    def setUp(self):
        super().setUp()
        self.base_fields['fields']['issuetype']['name'] = 'Story'
        self.parser = StoryParser(self.base_fields)

    @patch('jira_integration.models.Epic.objects.get')
    def test_create_or_update_story_with_existing_epic(self, mock_epic_get):
        mock_epic = Mock()
        mock_epic_get.return_value = mock_epic
        story_data = self.parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            expected_defaults = story_data.copy()
            epic_key = expected_defaults.pop('parent')
            
            self.parser.create_or_update(story_data)
            
            mock_epic_get.assert_called_once_with(id=epic_key)
            mock_create.assert_called_once_with(
                id=story_data['id'],
                defaults={**expected_defaults, 'parent': mock_epic}
            )

    @patch('jira_integration.models.Epic.objects.get')
    def test_create_or_update_story_with_missing_epic(self, mock_epic_get):
        mock_epic_get.side_effect = Epic.DoesNotExist()
        story_data = self.parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            with patch('builtins.print') as mock_print:
                self.parser.create_or_update(story_data)
                
                mock_print.assert_called_once_with(
                    f"Warning: Parent Epic EPIC-123 not found for Story {story_data['id']}"
                )
                mock_create.assert_called_once_with(
                    id=story_data['id'],
                    defaults=story_data
                )


class TaskParserTestCase(BaseParserTestCase):
    """Test cases specific to Task parsing"""
    
    def setUp(self):
        super().setUp()
        self.base_fields['key'] = 'TEST-123'
        self.base_fields['fields']['issuetype']['name'] = 'Access Ticket'
        self.parser = TaskParser(self.base_fields)

    def test_get_parent_existing_task_with_parent(self):
        """Test _get_parent when task exists and has a parent"""
        self.base_fields['fields']['issuelinks'] = []
        mock_parent = Mock()
        mock_parent.pk = 'STORY-999'
        mock_task = Mock()
        mock_task.parent = mock_parent

        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.return_value = mock_task
            result = self.parser._get_parent()
            self.assertEqual(result, 'STORY-999')

    def test_get_parent_existing_task_no_parent_raises_error(self):
        """Test _get_parent when task exists but has no parent"""
        self.base_fields['fields']['issuelinks'] = []
        mock_task = Mock()
        mock_task.parent = None

        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.return_value = mock_task
            with self.assertRaises(ValueError) as context:
                self.parser._get_parent()
            self.assertEqual(str(context.exception), "Tasks must have parents")

    def test_get_parent_multiple_links(self):
        """Test _get_parent with multiple parent links"""
        self.base_fields['fields']['issuelinks'] = [
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'TEST-124'}
            },
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'TEST-125'}
            }
        ]
        mock_task = Mock()
        mock_task.parent = None

        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()
            with self.assertRaises(ValueError) as context:
                self.parser._get_parent()
            self.assertEqual(
                str(context.exception),
                "Tasks cannot have multiple parents in the same project"
            )

    def test_get_parent_new_task_no_links(self):
        """Test _get_parent for new task with no links"""
        self.base_fields['fields']['issuelinks'] = []
        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()
            result = self.parser._get_parent()
            self.assertIsNone(result)
