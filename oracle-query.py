from celery import shared_task
from . import services
from jira_integration import constants


@shared_task(bind=True)
# TODO: Will need to remove request once we make it a task
def fetch_jira_epic_updates(request):
    """Subtask 1: Fetches updated issues from Jira"""
    services.get_jira_updated_issues(
        jql=constants.EPIC_JQL,
        fields=constants.EPIC_FIELDS,
        jira_type='epic'
    )


@shared_task(bind=True)
# TODO: Will need to remove request once we make it a task
def fetch_jira_story_updates(request):
    """Subtask 2: Fetches updated stories from Jira"""
    services.get_jira_updated_issues(
        jql=constants.STORY_JQL,
        fields=constants.STORY_FIELDS,
        jira_type='story'
    )


@shared_task(bind=True)
# TODO: Will need to remove request once we make it a task
def fetch_jira_task_updates(request):
    """Subtask 3: Fetches updated tasks from Jira"""
    services.get_jira_updated_issues(
        jql=constants.TASK_JQL,
        fields=constants.TASK_FIELDS,
        jira_type='task'
    )


@shared_task(bind=True)
# TODO: Will need to remove request once we make it a task
def process_jira_updates_and_changes(request):
    """
    In this process we are attempting to remove the webhook process and transition to
    using the jira JQL api process instead for any updates and story creations.
    """
    # Fetch all the jira epics and create them in db
    fetch_jira_epic_updates()
    # Fetch all the jira stories and create them in db
    fetch_jira_story_updates()
    # Fetch all the jira tasks and create them in db
    fetch_jira_task_updates()
