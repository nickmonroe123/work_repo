# services.py

def get_jira_updated_issues(jql: str, fields: str, jira_type: str):
    # Initialize client
    client = JiraClient()

    try:
        # Retrieve all the epics in the given time range
        jql_results = client.search_issues(jql, fields)
        create_or_update_records(jql_results, jira_type)

    except requests.exceptions.HTTPError as e:
        logger.error(f"Error occurred: {e}")
        if hasattr(e.response, 'status_code'):
            if e.response.status_code == 401:
                logger.error("Authentication failed. Please check your access token.")
            elif e.response.status_code == 403:
                logger.error("Permission denied. Please check your access permissions.")
            else:
                logger.error("An unexpected error occurred when getting jira updated issues.")
        else:
            logger.error("An unexpected error occurred when getting jira updated issues.")
        raise
