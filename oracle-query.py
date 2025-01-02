# tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from . import services
from jira_integration import constants
from celery.exceptions import MaxRetriesExceededError

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    acks_late=True
)
def fetch_jira_epic_updates():
    """Fetches updated issues from Jira"""
    try:
        logger.info("Starting epic updates fetch")
        services.get_jira_updated_issues(
            jql=constants.EPIC_JQL,
            fields=constants.EPIC_FIELDS,
            jira_type='epic'
        )
        logger.info("Completed epic updates fetch")
    except Exception as e:
        logger.error(f"Error in fetch_jira_epic_updates: {str(e)}", exc_info=True)
        raise

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    acks_late=True
)
def fetch_jira_story_updates():
    """Fetches updated stories from Jira"""
    try:
        logger.info("Starting story updates fetch")
        services.get_jira_updated_issues(
            jql=constants.STORY_JQL,
            fields=constants.STORY_FIELDS,
            jira_type='story'
        )
        logger.info("Completed story updates fetch")
    except Exception as e:
        logger.error(f"Error in fetch_jira_story_updates: {str(e)}", exc_info=True)
        raise

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60},
    acks_late=True
)
def fetch_jira_task_updates():
    """Fetches updated tasks from Jira"""
    try:
        logger.info("Starting task updates fetch")
        services.get_jira_updated_issues(
            jql=constants.TASK_JQL,
            fields=constants.TASK_FIELDS,
            jira_type='task'
        )
        logger.info("Completed task updates fetch")
    except Exception as e:
        logger.error(f"Error in fetch_jira_task_updates: {str(e)}", exc_info=True)
        raise

@shared_task(bind=True)
def process_jira_updates_and_changes():
    """
    Orchestrator task that manages the fetching and processing of Jira updates.
    Uses chord to ensure all fetch tasks complete before proceeding.
    """
    try:
        logger.info("Starting Jira updates process")
        
        # Create a group of tasks to run in parallel
        fetch_tasks = [
            fetch_jira_epic_updates.s(),
            fetch_jira_story_updates.s(),
            fetch_jira_task_updates.s()
        ]
        
        # Use chord to run tasks in parallel and ensure all complete
        from celery import chord
        chord(fetch_tasks)(process_completion.s())
        
    except Exception as e:
        logger.error(f"Error in process_jira_updates_and_changes: {str(e)}", exc_info=True)
        raise

@shared_task
def process_completion(results):
    """Callback task that runs after all fetch tasks complete"""
    logger.info("All Jira fetch tasks completed successfully")
    return results

# services.py
from typing import Dict, Optional
import requests
from requests.exceptions import RequestException
from django.conf import settings
from celery.utils.log import get_task_logger
from jira_integration.session import JiraSession
from jira_integration import constants
from jira_integration.parsers import create_or_update_records
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential

logger = get_task_logger(__name__)

@dataclass
class JiraResponse:
    """Data class to handle Jira API responses"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None

class JiraClientError(Exception):
    """Base exception for JiraClient errors"""
    pass

class JiraAuthenticationError(JiraClientError):
    """Raised when authentication fails"""
    pass

class JiraPermissionError(JiraClientError):
    """Raised when permission is denied"""
    pass

class JiraClient:
    """Class to abstract common API calls to Jira."""

    def __init__(self, base_url: str = None) -> None:
        self.session = JiraSession()
        self.logger = get_task_logger(__name__)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def search_issues(
        self,
        jql: str,
        fields: str,
        max_results: int = constants.MAX_JQL_RESULTS,
        start_at: int = 0
    ) -> JiraResponse:
        """
        Search for issues using JQL with retry logic and proper error handling.
        """
        try:
            params = {
                'jql': jql,
                'maxResults': max_results,
                'startAt': start_at,
                'fields': fields
            }
            
            self.logger.debug(f"Searching Jira issues with params: {params}")
            response = self.session.get('/rest/api/2/search', params=params)
            response.raise_for_status()
            
            return JiraResponse(
                success=True,
                data=response.json(),
                status_code=response.status_code
            )

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {str(e)}"
            self.logger.error(error_msg)
            
            if e.response.status_code == 401:
                raise JiraAuthenticationError("Authentication failed")
            elif e.response.status_code == 403:
                raise JiraPermissionError("Permission denied")
            
            return JiraResponse(
                success=False,
                error=error_msg,
                status_code=e.response.status_code
            )
            
        except RequestException as e:
            error_msg = f"Network error occurred: {str(e)}"
            self.logger.error(error_msg)
            return JiraResponse(success=False, error=error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error occurred: {str(e)}"
            self.logger.error(error_msg)
            return JiraResponse(success=False, error=error_msg)

def get_jira_updated_issues(jql: str, fields: str, jira_type: str):
    """
    Retrieve and process updated Jira issues with improved error handling and pagination.
    """
    client = JiraClient()
    logger.info(f"Starting to fetch {jira_type} issues")
    
    try:
        start_at = 0
        total = None
        processed_count = 0
        
        while total is None or start_at < total:
            response = client.search_issues(jql, fields, start_at=start_at)
            
            if not response.success:
                logger.error(f"Failed to fetch {jira_type} issues: {response.error}")
                raise JiraClientError(response.error)
            
            if total is None:
                total = response.data['total']
                logger.info(f"Total {jira_type} issues to process: {total}")
            
            create_or_update_records(response.data, jira_type)
            
            processed_count += len(response.data['issues'])
            start_at += constants.MAX_JQL_RESULTS
            
            logger.info(f"Processed {processed_count}/{total} {jira_type} issues")
            
    except (JiraAuthenticationError, JiraPermissionError) as e:
        logger.error(f"Authentication/Permission error: {str(e)}")
        raise
        
    except Exception as e:
        logger.error(f"Error processing {jira_type} issues: {str(e)}", exc_info=True)
        raise
    
    logger.info(f"Successfully completed processing {jira_type} issues")

# parsers.py improvements

from typing import Dict, List, Optional, Tuple
from django.utils.dateparse import parse_datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Epic, Story, Task
import logging

logger = logging.getLogger(__name__)

class ParserError(Exception):
    """Base exception for parser errors"""
    pass

class ValidationParserError(ParserError):
    """Raised when validation fails during parsing"""
    pass

class JiraParser:
    """Base class for parsing Jira issues with improved error handling."""

    def parse_with_validation(self) -> Tuple[Dict, bool]:
        """
        Parse and validate the data, returning both the parsed data and validation status.
        """
        try:
            parsed_data = self.parse()
            self.validate(parsed_data)
            return parsed_data, True
        except ValidationError as e:
            logger.error(f"Validation error for issue {self.data.get('key')}: {str(e)}")
            return {}, False
        except Exception as e:
            logger.error(f"Error parsing issue {self.data.get('key')}: {str(e)}")
            return {}, False

    def validate(self, parsed_data: Dict) -> None:
        """
        Validate the parsed data. Override in subclasses for specific validation rules.
        """
        required_fields = ['id', 'summary', 'status', 'issue_type']
        missing_fields = [field for field in required_fields if not parsed_data.get(field)]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

@transaction.atomic
def create_or_update_records(jira_json: Dict, jira_type: str):
    """Create or update records with improved error handling and atomic transactions."""
    parser_classes = {
        'epic': EpicParser,
        'story': StoryParser,
        'task': TaskParser
    }

    parser_class = parser_classes.get(jira_type)
    if not parser_class:
        raise ValueError(f"Unknown jira_type: {jira_type}")

    expected_type = parser_class.get_issue_type()
    success_count = 0
    error_count = 0

    try:
        for issue in jira_json.get('issues', []):
            if issue['fields']['issuetype']['name'] in expected_type:
                try:
                    with transaction.atomic():
                        parser = parser_class(issue)
                        parsed_data, is_valid = parser.parse_with_validation()
                        
                        if is_valid:
                            parser.create_or_update(parsed_data)
                            success_count += 1
                        else:
                            error_count += 1
                            
                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"Error processing {jira_type} issue {issue.get('key')}: {str(e)}",
                        exc_info=True
                    )
                    
        logger.info(
            f"Processed {jira_type} issues - "
            f"Success: {success_count}, Errors: {error_count}"
        )
        
    except Exception as e:
        logger.error(f"Fatal error processing {jira_type} issues: {str(e)}", exc_info=True)
        raise
