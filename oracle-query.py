from typing import Dict, List
from django.utils.dateparse import parse_datetime
from django.db import transaction
from .models import Epic, Story, Task
from jira_integration import constants

class JiraParser:
    """Base class for parsing Jira issues."""
    
    @staticmethod
    def parse_common_fields(issue: Dict) -> Dict:
        """Extract common fields from a Jira issue."""
        fields = issue['fields']
        return {
            'id': issue['key'],
            'status': fields['status']['name'],
            'issue_type': fields['issuetype']['name'],
            'close_date': parse_datetime(fields['resolutiondate']).date()
                         if fields.get('resolutiondate') else None
        }

    def parse(self, jira_response: Dict) -> List[Dict]:
        """Abstract method to be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement parse method")

    def create_or_update(self, parsed_data: Dict):
        """Abstract method to be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement create_or_update method")


class EpicParser(JiraParser):
    """Parser for Epic type Jira issues."""

    def parse(self, jira_response: Dict) -> List[Dict]:
        """Parse epic issues from Jira response."""
        epics = []
        for issue in jira_response.get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Epic':
                epic_data = self.parse_common_fields(issue)
                epics.append(epic_data)
        return epics

    def create_or_update(self, epic_data: Dict):
        """Create or update Epic records."""
        Epic.objects.update_or_create(
            id=epic_data['id'],
            defaults=epic_data
        )


class StoryParser(JiraParser):
    """Parser for Story type Jira issues."""

    def parse(self, jira_response: Dict) -> List[Dict]:
        """Parse story issues from Jira response."""
        stories = []
        for issue in jira_response.get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Story':
                story_data = self.parse_common_fields(issue)
                story_data['parent'] = issue['fields'].get(constants.EPIC_LINK, '')
                stories.append(story_data)
        return stories

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

    def parse(self, jira_response: Dict) -> List[Dict]:
        """Parse task issues from Jira response."""
        tasks = []
        for issue in jira_response.get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Change Ticket':
                task_data = self.parse_common_fields(issue)
                # Add task-specific fields
                task_data['close_code'] = (
                    issue['fields'].get(constants.CLOSE_CODE, {}).get('value')
                    if issue['fields'].get(constants.CLOSE_CODE) else None
                )
                tasks.append(task_data)
        return tasks

    def create_or_update(self, task_data: Dict):
        """Create or update Task records."""
        Task.objects.update_or_create(
            id=task_data['id'],
            defaults=task_data
        )


def create_or_update_records(jira_json: Dict, jira_type: str):
    """Create or update records in the database."""
    parser_map = {
        'epic': EpicParser(),
        'story': StoryParser(),
        'task': TaskParser()
    }

    parser = parser_map.get(jira_type)
    if not parser:
        raise ValueError(f"Unknown jira_type: {jira_type}")

    with transaction.atomic():
        parsed_data = parser.parse(jira_json)
        for item_data in parsed_data:
            parser.create_or_update(item_data)

    return
