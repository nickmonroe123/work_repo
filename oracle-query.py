# tests/test_parsers.py
from django.test import TestCase
from django.utils.dateparse import parse_datetime
from unittest.mock import Mock, patch
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
                'resolutiondate': '2024-01-01T12:00:00.000+0000'
            }
        }

class JiraParserTestCase(BaseParserTestCase):
    """Test cases for base JiraParser class"""

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

    def test_base_parse_method(self):
        """Test base parse method returns common fields"""
        parser = JiraParser(self.base_fields)
        result = parser.parse()
        self.assertEqual(result['id'], 'TEST-123')

class EpicParserTestCase(BaseParserTestCase):
    """Test cases for EpicParser class"""

    def setUp(self):
        super().setUp()
        self.base_fields['fields']['issuetype']['name'] = 'Epic'
        self.parser = EpicParser(self.base_fields)

    def test_get_issue_type(self):
        """Test get_issue_type returns correct types"""
        self.assertEqual(EpicParser.get_issue_type(), ['Epic'])

    def test_parse_epic(self):
        """Test parsing epic data"""
        result = self.parser.parse()
        self.assertEqual(result['issue_type'], 'EPIC')

    @patch('jira_integration.models.Epic.objects')
    def test_create_or_update_epic(self, mock_epic_objects):
        """Test creating/updating epic records"""
        epic_data = self.parser.parse()
        self.parser.create_or_update(epic_data)
        
        mock_epic_objects.update_or_create.assert_called_once_with(
            id=epic_data['id'],
            defaults=epic_data
        )

class StoryParserTestCase(BaseParserTestCase):
    """Test cases for StoryParser class"""

    def setUp(self):
        super().setUp()
        self.base_fields['fields']['issuetype']['name'] = 'Story'
        self.base_fields['fields'][constants.EPIC_LINK] = 'EPIC-123'
        self.parser = StoryParser(self.base_fields)

    def test_get_issue_type(self):
        """Test get_issue_type returns correct types"""
        self.assertEqual(StoryParser.get_issue_type(), ['Story'])

    def test_parse_story_with_epic(self):
        """Test parsing story data with epic link"""
        result = self.parser.parse()
        self.assertEqual(result['issue_type'], 'STORY')
        self.assertEqual(result['parent'], 'EPIC-123')

    def test_parse_story_without_epic(self):
        """Test parsing story data without epic link"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields'].pop(constants.EPIC_LINK)
        parser = StoryParser(data)
        
        result = parser.parse()
        self.assertEqual(result['parent'], '')

    def test_get_parent_method(self):
        """Test _get_parent method"""
        self.assertEqual(self.parser._get_parent(), 'EPIC-123')

    @patch('jira_integration.models.Epic.objects.get')
    def test_create_or_update_story_with_existing_epic(self, mock_epic_get):
        """Test creating story with existing epic"""
        mock_epic = Mock()
        mock_epic_get.return_value = mock_epic
        
        story_data = self.parser.parse()
        
        with patch('jira_integration.models.Story.objects.update_or_create') as mock_create:
            self.parser.create_or_update(story_data)
            
            expected_defaults = {**story_data}
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
                mock_create.assert_called_once()

class TaskParserTestCase(BaseParserTestCase):
    """Test cases for TaskParser class"""

    def setUp(self):
        super().setUp()
        self.base_fields['fields'].update({
            'issuetype': {'name': 'Access Ticket'},
            constants.ASSIGNED_GROUP: {'value': 'IT'},
            constants.CLOSE_CODE: {'value': 'COMPLETED'},
            'issuelinks': [{
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'STORY-123'}
            }]
        })
        self.parser = TaskParser(self.base_fields)

    def test_get_issue_type(self):
        """Test get_issue_type returns correct types"""
        expected_types = [
            'Access Ticket', 'Delete Ticket',
            'Appeal Ticket', 'Change Ticket'
        ]
        self.assertEqual(TaskParser.get_issue_type(), expected_types)

    def test_parse_task_full_data(self):
        """Test parsing task with all fields"""
        result = self.parser.parse()
        
        self.assertEqual(result['issue_type'], 'ACCESS_TICKET')
        self.assertEqual(result['business_unit'], 'IT')
        self.assertEqual(result['close_code'], 'COMPLETED')
        self.assertEqual(result['parent_key'], 'STORY-123')

    def test_parse_task_without_close_code(self):
        """Test parsing task without close code"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields'].pop(constants.CLOSE_CODE)
        parser = TaskParser(data)
        
        result = parser.parse()
        self.assertIsNone(result['close_code'])

    def test_get_parent_with_single_link(self):
        """Test _get_parent with single valid parent link"""
        result = self.parser._get_parent()
        self.assertEqual(result, 'STORY-123')

    def test_get_parent_with_multiple_links(self):
        """Test _get_parent with multiple parent links"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields']['issuelinks'] = [
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'STORY-123'}
            },
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'STORY-124'}
            }
        ]
        parser = TaskParser(data)
        
        with self.assertRaises(ValueError) as context:
            parser._get_parent()
        self.assertEqual(
            str(context.exception),
            "Tasks cannot have multiple parents in the same project"
        )

    def test_get_parent_with_no_links_existing_task(self):
        """Test _get_parent with no links but existing task"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields']['issuelinks'] = []
        parser = TaskParser(data)
        
        # Mock existing task with parent
        mock_task = Mock()
        mock_task.parent = Mock()
        mock_task.parent.pk = 'STORY-999'
        
        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.return_value = mock_task
            result = parser._get_parent()
            self.assertEqual(result, 'STORY-999')

    def test_get_parent_with_no_links_new_task(self):
        """Test _get_parent with no links and new task"""
        data = self.base_fields.copy()
        data['fields'] = data['fields'].copy()
        data['fields']['issuelinks'] = []
        parser = TaskParser(data)
        
        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()
            result = parser._get_parent()
            self.assertIsNone(result)

    @patch('jira_integration.models.Story.objects.get')
    def test_create_or_update_task_with_existing_parent(self, mock_story_get):
        """Test creating task with existing parent story"""
        mock_story = Mock()
        mock_story_get.return_value = mock_story
        
        task_data = self.parser.parse()
        
        with patch('jira_integration.models.Task.objects.update_or_create') as mock_create:
            self.parser.create_or_update(task_data)
            
            expected_defaults = {**task_data}
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
        
        task_data = self.parser.parse()
        
        with patch('jira_integration.models.Task.objects.update_or_create') as mock_create:
            with patch('builtins.print') as mock_print:
                self.parser.create_or_update(task_data)
                
                mock_print.assert_called_once_with(
                    f"Warning: Parent Issue STORY-123 not found for Task {task_data['id']}"
                )
                mock_create.assert_called_once()

class CreateOrUpdateRecordsTestCase(BaseParserTestCase):
    """Test cases for create_or_update_records function"""

    def test_create_or_update_records_unknown_type(self):
        """Test handling of unknown jira_type"""
        with self.assertRaises(ValueError) as context:
            create_or_update_records({}, 'unknown')
        self.assertEqual(
            str(context.exception),
            "Unknown jira_type: unknown"
        )

    def test_create_or_update_records_epic(self):
        """Test creating epic records"""
        jira_json = {
            'issues': [self.base_fields]
        }
        self.base_fields['fields']['issuetype']['name'] = 'Epic'
        
        with patch.object(EpicParser, 'create_or_update') as mock_create:
            create_or_update_records(jira_json, 'epic')
            mock_create.assert_called_once()

    def test_create_or_update_records_empty_issues(self):
        """Test handling empty issues list"""
        jira_json = {'issues': []}
        create_or_update_records(jira_json, 'epic')

    def test_create_or_update_records_wrong_type(self):
        """Test handling issues of wrong type"""
        jira_json = {
            'issues': [self.base_fields]
        }
        self.base_fields['fields']['issuetype']['name'] = 'Wrong Type'
        
        create_or_update_records(jira_json, 'epic')

    @patch.object(EpicParser, 'create_or_update')
    @patch.object(EpicParser, 'parse')
    def test_create_or_update_records_parsing_flow(self, mock_parse, mock_create):
        """Test complete parsing and creation flow"""
        jira_json = {
            'issues': [self.base_fields]
        }
        self.base_fields['fields']['issuetype']['name'] = 'Epic'
        
        parsed_data = {'id': 'TEST-123', 'summary': 'Test'}
        mock_parse.return_value = parsed_data
        
        create_or_update_records(jira_json, 'epic')
        
        mock_parse.assert_called_once()
        mock_create.assert_called_once_with(parsed_data)
