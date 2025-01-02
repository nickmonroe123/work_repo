from celery import shared_task
from celery.utils.log import get_task_logger
from . import services
from jira_integration import constants

logger = get_task_logger(__name__)

class JiraUpdateError(Exception):
    """Custom exception for Jira update process failures"""
    pass

@shared_task
def fetch_jira_epic_updates():
    """Subtask 1: Fetches updated issues from Jira"""
    try:
        logger.info("Starting epic updates fetch")
        services.get_jira_updated_issues(
            jql=constants.EPIC_JQL,
            fields=constants.EPIC_FIELDS,
            jira_type='epic'
        )
        logger.info("Completed epic updates fetch")
        return True
    except Exception as e:
        logger.error(f"Error in fetch_jira_epic_updates: {str(e)}")
        raise JiraUpdateError(f"Epic update failed: {str(e)}")


@shared_task
def fetch_jira_story_updates():
    """Subtask 2: Fetches updated stories from Jira"""
    try:
        logger.info("Starting story updates fetch")
        services.get_jira_updated_issues(
            jql=constants.STORY_JQL,
            fields=constants.STORY_FIELDS,
            jira_type='story'
        )
        logger.info("Completed story updates fetch")
        return True
    except Exception as e:
        logger.error(f"Error in fetch_jira_story_updates: {str(e)}")
        raise JiraUpdateError(f"Story update failed: {str(e)}")


@shared_task
def fetch_jira_task_updates():
    """Subtask 3: Fetches updated tasks from Jira"""
    try:
        logger.info("Starting task updates fetch")
        services.get_jira_updated_issues(
            jql=constants.TASK_JQL,
            fields=constants.TASK_FIELDS,
            jira_type='task'
        )
        logger.info("Completed task updates fetch")
        return True
    except Exception as e:
        logger.error(f"Error in fetch_jira_task_updates: {str(e)}")
        raise JiraUpdateError(f"Task update failed: {str(e)}")


@shared_task
def process_jira_updates_and_changes():
    """
    Main task that processes Jira updates sequentially.
    If any subtask fails, the entire process will fail.
    
    Execution order:
    1. Fetch Epics
    2. Fetch Stories
    3. Fetch Tasks
    """
    try:
        logger.info("Starting Jira updates process")
        
        # Step 1: Fetch Epics
        epic_result = fetch_jira_epic_updates.apply()
        if not epic_result.successful():
            raise JiraUpdateError("Epic update process failed")
        
        # Step 2: Fetch Stories
        story_result = fetch_jira_story_updates.apply()
        if not story_result.successful():
            raise JiraUpdateError("Story update process failed")
        
        # Step 3: Fetch Tasks
        task_result = fetch_jira_task_updates.apply()
        if not task_result.successful():
            raise JiraUpdateError("Task update process failed")
        
        logger.info("All Jira update processes completed successfully")
        return True
        
    except JiraUpdateError as e:
        logger.error(f"Jira update process failed: {str(e)}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in Jira update process: {str(e)}")
        raise
