from typing import Dict, List, Optional
from django.utils.dateparse import parse_datetime
from django.db import transaction
from .models import Epic, Story, Task, Issue
from jira_integration import constants

class JiraParser:
    """Base class for parsing Jira issues."""
    
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
            'status': fields['status']['name'],
            'issue_type': fields['issuetype']['name'],
            'close_date': parse_datetime(fields['resolutiondate']).date()
                         if fields.get('resolutiondate') else None
        }

    def parse(self) -> Dict:
        """Base parsing method to be extended by child classes."""
        return self.parse_common_fields(self.data)

    def _get_parent(self) -> Optional[str]:
        """Abstract method to be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement _get_parent method")

    def create_or_update(self, parsed_data: Dict):
        """Abstract method to be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement create_or_update method")


class EpicParser(JiraParser):
    """Parser for Epic type Jira issues."""
    
    @classmethod
    def get_issue_type(cls) -> str:
        return 'Epic'

    def parse(self) -> Dict:
        """Parse epic issues from Jira response."""
        return super().parse()

    def _get_parent(self) -> Optional[str]:
        """Epics don't have parents."""
        return None

    def create_or_update(self, epic_data: Dict):
        """Create or update Epic records."""
        Epic.objects.update_or_create(
            id=epic_data['id'],
            defaults=epic_data
        )


class StoryParser(JiraParser):
    """Parser for Story type Jira issues."""
    
    @classmethod
    def get_issue_type(cls) -> str:
        return 'Story'

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
        from django.db import Error as DBError
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Remove epic_key from defaults since it's not a model field
            epic_key = story_data.pop('parent', None)
            
            logger.debug(f"Processing story {story_data['id']} with epic_key {epic_key}")

            # First, try to find the parent epic
            parent_epic = None
            if epic_key:
                try:
                    parent_epic = Epic.objects.select_for_update().get(id=epic_key)
                    logger.debug(f"Found parent epic {epic_key}")
                except Epic.DoesNotExist:
                    logger.warning(f"Parent Epic {epic_key} not found for Story {story_data['id']}")

            # Prepare the defaults
            defaults = story_data.copy()
            if parent_epic:
                defaults['parent'] = parent_epic
            
            logger.debug(f"Attempting to update/create story with defaults: {defaults}")

            # Create or update the story with a timeout
            from django.db import connection
            connection.execute_wrapper = None  # Reset any existing wrappers
            
            story, created = Story.objects.select_for_update().update_or_create(
                id=story_data['id'],
                defaults=defaults
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} story {story.id} successfully")
            
            return story

        except DBError as e:
            logger.error(f"Database error while processing story {story_data['id']}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while processing story {story_data['id']}: {str(e)}")
            raise


class TaskParser(JiraParser):
    """Parser for Task type Jira issues."""
    
    @classmethod
    def get_issue_type(cls) -> str:
        return 'Change Ticket'

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
                existing_task = Issue.objects.get(jira_id=self.data['key'])
                if existing_task.parent:
                    return existing_task.parent.pk
                else:
                    if num_links > 1:
                        raise ValueError("Tasks cannot have multiple parents in the same project")
                    raise ValueError("Tasks must have parents")
            except Issue.DoesNotExist:
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
                parent = Issue.objects.get(jira_id=parent_key)
            except Issue.DoesNotExist:
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

    with transaction.atomic():
        for issue in jira_json.get('issues', []):
            if issue['fields']['issuetype']['name'] == expected_type:
                parser = parser_class(issue)
                parsed_data = parser.parse()
                parser.create_or_update(parsed_data)

    return
