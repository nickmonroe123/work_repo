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

    @classmethod
    def get_issue_type(cls) -> str:
        """Abstract method to return the issue type this parser handles."""
        raise NotImplementedError("Subclasses must implement get_issue_type method")

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
