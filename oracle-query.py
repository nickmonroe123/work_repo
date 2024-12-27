from typing import Dict, List, Optional
from datetime import datetime
from django.utils.timezone import make_aware

class JiraParser:
    @staticmethod
    def parse_common_fields(issue: Dict) -> Dict:
        """Extract common fields from a Jira issue."""
        fields = issue['fields']
        return {
            'id': issue['key'],
            'status': fields['status']['name'],
            'issue_type': fields['issuetype']['name'],
            'close_date': make_aware(datetime.strptime(fields['resolutiondate'], '%Y-%m-%dT%H:%M:%S.%f%z')) 
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
                # You might need to add logic here to link to parent epic
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
                    issue['fields'].get('customfield_16748', {}).get('value')
                    if issue['fields'].get('customfield_16748') else None
                )
                tasks.append(task_data)
        return tasks

def create_or_update_records(epics_json: Dict, stories_json: Dict, tasks_json: Dict):
    """Create or update records in the database."""
    from django.db import transaction
    
    with transaction.atomic():
        # Process epics
        epic_records = []
        for epic_data in JiraParser.parse_epics(epics_json):
            epic, created = Epic.objects.update_or_create(
                id=epic_data['id'],
                defaults=epic_data
            )
            epic_records.append(epic)

        # Process stories
        story_records = []
        for story_data in JiraParser.parse_stories(stories_json):
            # You might need to add logic here to determine the parent epic
            story, created = Story.objects.update_or_create(
                id=story_data['id'],
                defaults=story_data
            )
            story_records.append(story)

        # Process tasks
        task_records = []
        for task_data in JiraParser.parse_tasks(tasks_json):
            # You might need to add logic here to determine the parent story
            task, created = Task.objects.update_or_create(
                id=task_data['id'],
                defaults=task_data
            )
            task_records.append(task)

    return epic_records, story_records, task_records
