from typing import Dict, List, Optional
from django.utils.dateparse import parse_datetime
from django.db import transaction
from .models import Epic, Story, Task, Issue
from jira_integration import constants


class JiraParser:
    """
    Base class for parsing Jira issues.
    custom JQL fields: https://chalk.charter.com/display/JIRAREQ/Jira+Custom+Fields
    """
    def __init__(self, data: Dict):
        self.data = data

    @staticmethod
    def parse_common_fields(issue: Dict) -> Dict:
        """Extract common fields from a Jira issue."""
        fields = issue['fields']
        return {
            'id': issue['key'],
            'summary': fields['summary'],
            'status': fields['status']['name'].upper().replace(' ', '_'),
            'issue_type': fields['issuetype']['name'].upper().replace(' ', '_'),
            'close_date': parse_datetime(fields['resolutiondate']).date()
            if fields.get('resolutiondate') else None
        }

    def parse(self) -> Dict:
        """Base parsing method to be extended by child classes."""
        return self.parse_common_fields(self.data)


class EpicParser(JiraParser):
    """Parser for Epic type Jira issues."""

    @classmethod
    def get_issue_type(cls) -> list:
        return ['Epic']

    def parse(self) -> Dict:
        """Parse epic issues from Jira response."""
        return super().parse()

    def create_or_update(self, epic_data: Dict):
        """Create or update Epic records."""
        Epic.objects.update_or_create(
            id=epic_data['id'],
            defaults=epic_data
        )


class StoryParser(JiraParser):
    """Parser for Story type Jira issues."""

    @classmethod
    def get_issue_type(cls) -> list:
        return ['Story']

    def parse(self) -> Dict:
        """Parse story issues from Jira response."""
        parsed_data = super().parse()
        parsed_data['parent'] = self.data['fields'].get(constants.EPIC_LINK, '')
        return parsed_data

    def _get_parent(self) -> Optional[str]:
        """Get parent epic key."""
        return self.data['fields'].get(constants.EPIC_LINK)

    def create_or_update(self, story_data: Dict):
        """Create or update Story records."""
        # Remove epic_key from defaults since it's not a model field
        epic_key = story_data.pop('parent', None)

        # First, try to find the parent epic
        parent_epic = None
        if epic_key:
            try:
                parent_epic = Epic.objects.get(id=epic_key)
            except Epic.DoesNotExist:
                print(f"Warning: Parent Epic {epic_key} not found for Story {story_data['id']}")

        # Create or update the story
        Story.objects.update_or_create(
            id=story_data['id'],
            defaults={**story_data, 'parent': parent_epic} if parent_epic else story_data
        )


class TaskParser(JiraParser):
    """Parser for Task type Jira issues."""

    @classmethod
    def get_issue_type(cls) -> list:
        return ['Access Ticket', 'Delete Ticket', 'Appeal Ticket', 'Change Ticket']

    def parse(self) -> Dict:
        """Parse task issues from Jira response."""
        parsed_data = super().parse()

        # Add business unit from assigned group
        parsed_data['business_unit'] = self.data['fields'][constants.ASSIGNED_GROUP]['value']

        # Add close code
        close_code = self.data['fields'].get(constants.CLOSE_CODE)
        parsed_data['close_code'] = close_code['value'] if close_code else None

        # Add parent information
        parsed_data['parent_key'] = self._get_parent()

        return parsed_data

    def _get_parent(self) -> Optional[str]:
        """
        Get parent issue key following specific business rules:
        1. Must be a parent-child relationship
        2. Must be in the same project
        3. Can only have one parent in the same project
        """
        # Filter parent-child relationships in the same project
        parent_child_issue_links = [
            d for d in self.data['fields']['issuelinks']
            if (d['type']['inward'] == 'is child task of' and
                'inwardIssue' in d and
                d['inwardIssue']['key'].startswith(self.data['key'].split('-')[0]))
        ]

        num_links = len(parent_child_issue_links)
        if num_links != 1:
            try:
                # Check if task already exists and has a parent
                existing_task = Story.objects.get(id=self.data['key'])
                if existing_task.parent:
                    return existing_task.parent.pk
                else:
                    if num_links > 1:
                        raise ValueError("Tasks cannot have multiple parents in the same project")
                    raise ValueError("Tasks must have parents")
            except Story.DoesNotExist:
                # New task with no parent - allowed for initial creation
                return None

        return parent_child_issue_links[0]['inwardIssue']['key']

    def create_or_update(self, task_data: Dict):
        """Create or update Task records."""
        parent_key = task_data.pop('parent_key', None)

        # Find parent issue if parent key exists
        parent = None
        if parent_key:
            try:
                parent = Story.objects.get(id=parent_key)
            except Story.DoesNotExist:
                print(f"Warning: Parent Issue {parent_key} not found for Task {task_data['id']}")

        Task.objects.update_or_create(
            id=task_data['id'],
            defaults={**task_data, 'parent': parent} if parent else task_data
        )


def create_or_update_records(jira_json: Dict, jira_type: str):
    """Create or update records in the database."""
    parser_classes = {
        'epic': EpicParser,
        'story': StoryParser,
        'task': TaskParser
    }

    parser_class = parser_classes.get(jira_type)
    if not parser_class:
        raise ValueError(f"Unknown jira_type: {jira_type}")

    expected_type = parser_class.get_issue_type()

    for issue in jira_json.get('issues', []):
        if issue['fields']['issuetype']['name'] in expected_type:
            parser = parser_class(issue)
            parsed_data = parser.parse()
            parser.create_or_update(parsed_data)

    return

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
                    'key': 'TEST-1234',
                    'fields': {'project': {'key': 'TEST'}}
                }
            }]
        })
        self.parser = TaskParser(self.base_fields)

    def test_get_parent_with_single_link(self):
        """Test _get_parent with single valid parent link"""
        self.base_fields['key'] = 'TEST-123'  # Ensure key matches project
        result = self.parser._get_parent()
        self.assertEqual(result, 'TEST-1234')

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

    def test_parse_task_full_data(self):
        """Test parsing task with all fields"""
        self.base_fields['key'] = 'TEST-123'
        result = self.parser.parse()

        self.assertEqual(result['issue_type'], 'ACCESS_TICKET')
        self.assertEqual(result['business_unit'], 'IT')
        self.assertEqual(result['close_code'], 'COMPLETED')
        self.assertEqual(result['parent_key'], 'TEST-1234')

    @patch('jira_integration.models.Story.objects.get')
    def test_create_or_update_task_with_existing_parent(self, mock_story_get):
        """Test creating task with existing parent story"""
        mock_story = Mock()
        mock_story_get.return_value = mock_story

        self.base_fields['key'] = 'TEST-123'
        task_data = self.parser.parse()

        with patch('jira_integration.models.Task.objects.update_or_create') as mock_create:
            expected_defaults = task_data.copy()
            parent_key = expected_defaults.pop('parent_key')

            self.parser.create_or_update(task_data)

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
                # Verify create called with correct data
                expected_defaults = task_data.copy()
                expected_defaults.pop('parent_key')

                self.parser.create_or_update(task_data)

                mock_print.assert_called_once_with(
                    f"Warning: Parent Issue TEST-1234 not found for Task {task_data['id']}"
                )

                mock_create.assert_called_once_with(
                    id=task_data['id'],
                    defaults=expected_defaults
                )


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

    def test_parser_issue_types(self):
        """Test get_issue_type for all parser classes"""
        # Test Epic parser
        self.assertEqual(EpicParser.get_issue_type(), ['Epic'])

        # Test Story parser
        self.assertEqual(StoryParser.get_issue_type(), ['Story'])

        # Test Task parser
        expected_task_types = [
            'Access Ticket',
            'Delete Ticket',
            'Appeal Ticket',
            'Change Ticket'
        ]
        self.assertEqual(TaskParser.get_issue_type(), expected_task_types)

Can you do the same thing that I requested for the last two requests? Parameterize, condense, but keep 100% coverage!
