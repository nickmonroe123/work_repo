from django.db import models
from typing import TypedDict, Optional
from datetime import datetime

# API Response Structures
class JiraFields(TypedDict):
    status: dict
    issuetype: dict
    customfield_25053: Optional[str]  # close_date
    customfield_16748: Optional[dict]  # close_code

class JiraResponse(TypedDict):
    id: str
    fields: JiraFields

# Base Abstract Model
class Issue(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    status = models.CharField(max_length=50)
    issue_type = models.CharField(max_length=50)
    close_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

# Concrete Models
class Epic(Issue):
    class Meta:
        db_table = 'jira_epic'

class Story(Issue):
    parent = models.ForeignKey(
        Epic,
        on_delete=models.CASCADE,
        related_name='stories'
    )

    class Meta:
        db_table = 'jira_story'

class Task(Issue):
    parent = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    business_unit = models.CharField(max_length=100)
    close_code = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'jira_task'

# Data Transfer Object
class IssueData:
    @staticmethod
    def from_jira_response(response: JiraResponse) -> dict:
        fields = response['fields']
        return {
            'id': response['id'],
            'status': fields['status']['name'],
            'issue_type': fields['issuetype']['name'],
            'close_date': fields.get('customfield_25053'),
        }
