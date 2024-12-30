from typing import Dict, List
from django.utils.dateparse import parse_datetime
from .models import Epic, Story, Task
from jira_integration import constants

class JiraParser:
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

    @staticmethod
    def parse_epics(jira_response: Dict) -> List[Dict]:
        """Parse epic issues from Jira response."""
        epics = []
        for issue in jira_response.get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Epic':
                epic_data = JiraParser.parse_common_fields(issue)
                epics.append(epic_data)
        return epics

    @staticmethod
    def parse_stories(jira_response: Dict) -> List[Dict]:
        """Parse story issues from Jira response."""
        stories = []
        for issue in jira_response.get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Story':
                story_data = JiraParser.parse_common_fields(issue)
                story_data['parent'] = issue['fields'].get(constants.EPIC_LINK, '')
                stories.append(story_data)
        return stories

    @staticmethod
    def parse_tasks(jira_response: Dict) -> List[Dict]:
        """Parse task issues from Jira response."""
        tasks = []
        for issue in jira_response.get('issues', []):
            if issue['fields']['issuetype']['name'] == 'Change Ticket':
                task_data = JiraParser.parse_common_fields(issue)
                # Add task-specific fields
                task_data['close_code'] = (
                    issue['fields'].get(constants.CLOSE_CODE, {}).get('value')
                    if issue['fields'].get(constants.CLOSE_CODE) else None
                )
                tasks.append(task_data)
        return tasks

def create_or_update_records(jira_json: Dict, jira_type: str):
    """Create or update records in the database."""
    from django.db import transaction

    with transaction.atomic():
        # Process epics
        if jira_type == "epic":
            for epic_data in JiraParser.parse_epics(jira_json):
                Epic.objects.update_or_create(
                    id=epic_data['id'],
                    defaults=epic_data
                )

        elif jira_type == "story":
            # Process stories
            for story_data in JiraParser.parse_stories(jira_json):
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

        elif jira_type == "task":
            print("HI")
            # Process tasks
            for task_data in JiraParser.parse_tasks(jira_json):
                Task.objects.update_or_create(
                    id=task_data['id'],
                    defaults=task_data
                )

    return

Can you turn this into a 4 class based system. Jira parser, epic parser, story parser, and task parser and split out the three if statemtns and parsing functions into their own respecitvie class!
create_or_update_records has all three type go through it still. just cleaner
