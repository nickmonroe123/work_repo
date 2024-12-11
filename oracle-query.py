import os
from re import search

import requests
from urllib.parse import urljoin

# Jira
JIRA_ACCESS_TOKEN = "*"
JIRA_URL = os.getenv('JIRA_URL', '*')

class BaseURLSession(requests.Session):
    """Session class with base URL support."""

    def __init__(self, base_url):
        self.base_url = base_url
        super().__init__()

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.base_url, url)
        try:
            resp = super().request(method, url, *args, **kwargs)
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            e.args += (resp.text,)
            raise e
        return resp


class JiraSession(BaseURLSession):
    """Jira session with personal access token authentication."""

    def __init__(self, base_url, access_token):
        super().__init__(base_url=base_url)

        # Set up authentication headers
        self.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })


class JiraClient:
    """Jira API client with common operations."""
    # init the three datasets
    jira_epics = []
    jira_stories = []
    jira_tasks = []
    jira_dataset = []

    def __init__(self, base_url: str, access_token: str) -> None:
        self.session = JiraSession(base_url, access_token)

    def get_issue(self, issue_id: str):
        """Gets a specific issue by ID."""
        return self.session.get(f'/rest/api/2/issue/{issue_id}').json()

    def search_issues(self, jql: str, fields: str, max_results: int = 50, start_at: int = 0):
        """Search for issues using JQL."""
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at,
            'fields': fields
        }
        return self.session.get('/rest/api/2/search', params=params).json()

    def extract_values(self, data):
        try:
            # Check if data exists and has 'issues' key
            if not data or not isinstance(data, dict):
                return []

            issues = data.get('issues', [])
            if not issues:
                return []

            result = []
            for index, issue in enumerate(issues):
                try:
                    # Use get() method with default values to handle missing keys
                    issue_data = {
                        'id': issue.get('id', 'ERROR'),
                        'issue_type': (
                            issue.get('fields', {})
                            .get('issuetype', {})
                            .get('name', 'ERROR')
                        ),
                        'status_name': (
                            issue.get('fields', {})
                            .get('status', {})
                            .get('name', 'ERROR')
                        ),
                        'closed_date': issue.get('customfield_25053', 'ERROR'),
                        'close_code': issue.get('customfield_16748', {}).get('value', 'None')
                    }
                    result.append(issue_data)
                except Exception as e:
                    # Handle errors for individual records without failing the entire process
                    print(f"Warning: Error processing issue at index {index}: {str(e)}")
                    result.append({
                        'id': 'ERROR',
                        'status_name': 'ERROR',
                        'error': str(e)
                    })

            return result

        except Exception as e:
            return []


def main():
    # Initialize client
    jira_client = JiraClient(
        base_url=JIRA_URL,
        access_token=JIRA_ACCESS_TOKEN
    )

    try:
        # Retrieve all the epics in the given time range
        epic_results = jira_client.search_issues(
            'project = DPCP AND updated >= -12h AND issuetype  = EPIC',
            'status,issuetype'
        )
        jira_client.jira_dataset += jira_client.extract_values(epic_results)

        # Retrieve all the stories in the given time range
        story_results = jira_client.search_issues(
            'project = DPCP AND updated >= -12h AND issuetype  = STORY',
            'status,issuetype,customfield_25053,customfield_16748'
        )
        jira_client.jira_dataset += jira_client.extract_values(story_results)

        # Retrieve all the tasks in the given time range
        task_results = jira_client.search_issues(
            'project = DPCP AND updated >= -120h AND (issuetype = "Access Ticket" OR issuetype = "Delete Ticket" '
            'OR issuetype = "Appeal Ticket" OR issuetype = "Change Ticket") AND status != New',
            'status,issuetype,customfield_25053,customfield_16748'
        )
        jira_client.jira_dataset += jira_client.extract_values(task_results)
        # update: jira id, close date, close code, status
        # (check if this updated endpoint has created the story in the last 12 hours as well or just updated)
        for record in jira_client.jira_dataset:
            print(record)

    except requests.exceptions.HTTPError as e:
        print(f"Error occurred: {e}")
        if '401' in str(e):
            print("Authentication failed. Please check your access token.")
        elif '403' in str(e):
            print("Permission denied. Please check your access permissions.")
        else:
            print("An unexpected error occurred.")


if __name__ == "__main__":
    main()
