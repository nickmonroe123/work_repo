"""Services for the Jira app."""
import requests

from jira_integration.session import JiraSession
from jira_integration import constants
from jira_integration.parsers import create_or_update_records


class JiraClient:
    """Class to abstract common API calls to Jira."""

    def __init__(self, base_url: str = None) -> None:
        # self.session = JiraSession(base_url)
        self.session = JiraSession()


    def search_issues(self, jql: str, fields: str, max_results: int = constants.MAX_JQL_RESULTS, start_at: int = 0):
        """Search for issues using JQL."""
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at,
            'fields': fields
        }
        return self.session.get('/rest/api/2/search', params=params).json()


def get_jira_updated_issues(jql: str, fields: str, jira_type: str):
    # Initialize client
    client = JiraClient()

    try:
        # Retrieve all the epics in the given time range
        jql_results = client.search_issues(jql, fields)
        create_or_update_records(jql_results, jira_type)

    except requests.exceptions.HTTPError as e:
        print(f"Error occurred: {e}")
        if '401' in str(e):
            print("Authentication failed. Please check your access token.")
        elif '403' in str(e):
            print("Permission denied. Please check your access permissions.")
        else:
            print("An unexpected error occurred.")
