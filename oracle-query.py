I'll help you create a parser to transform the JSON responses into Django model records. Let's create a structured way to handle this data. First, let's create a parser class that will handle the transformation:

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

Now, you can modify your `get_jira_updated_issues` function to use this parser:<antArtifact identifier="jira-update" type="application/vnd.ant.code" language="python" title="Updated Jira Issue Retrieval">

def get_jira_updated_issues(epic_jql: str, story_jql: str, task_jql: str, fields: str):
    """
    Retrieve and process Jira issues of different types.
    
    Args:
        epic_jql (str): JQL query for epics
        story_jql (str): JQL query for stories
        task_jql (str): JQL query for tasks
        fields (str): Comma-separated list of fields to retrieve
    """
    client = JiraClient()

    try:
        # Retrieve all issue types
        epic_results = client.search_issues(epic_jql, fields)
        story_results = client.search_issues(story_jql, fields)
        task_results = client.search_issues(task_jql, fields)

        # Create or update records
        epic_records, story_records, task_records = create_or_update_records(
            epic_results, story_results, task_results
        )

        print(f"Processed {len(epic_records)} epics, {len(story_records)} stories, "
              f"and {len(task_records)} tasks")

    except requests.exceptions.HTTPError as e:
        print(f"Error occurred: {e}")
        if '401' in str(e):
            print("Authentication failed. Please check your access token.")
        elif '403' in str(e):
            print("Permission denied. Please check your access permissions.")
        else:
            print("An unexpected error occurred.")

This code provides:

1. A `JiraParser` class that handles parsing different types of issues (Epics, Stories, and Tasks)
2. Methods to extract common fields and type-specific fields
3. A transaction-safe way to create or update records in the database
4. Error handling for API requests

To use this code:

```python
# Example usage
fields = "issuetype,status,resolutiondate,customfield_16748"
epic_jql = "project = DPCP AND issuetype = Epic"
story_jql = "project = DPCP AND issuetype = Story"
task_jql = "project = DPCP AND issuetype = 'Change Ticket'"

get_jira_updated_issues(epic_jql, story_jql, task_jql, fields)
```

A few notes:
1. The code assumes that the parent-child relationships between Epics, Stories, and Tasks are maintained in Jira. You might need to add additional fields to track these relationships.
2. You might want to add more error handling and logging.
3. The code uses Django's transaction management to ensure data consistency.
4. You might need to adjust the field mappings based on your specific Jira configuration.

Would you like me to add any specific functionality or modify any part of this implementation?
