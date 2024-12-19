@shared_task
def process_jira_updates_and_changes():
    "Runs every x hours to track changes and updates. Replacement of webhook"

    services.get_jira_updated_issues()

    # From here on we need to process the updated records (update, create, etc)
    return
