import os
import requests
from urllib.parse import urljoin

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

    def __init__(self, base_url: str, access_token: str) -> None:
        self.session = JiraSession(base_url, access_token)

    def get_issue(self, issue_id: str):
        """Gets a specific issue by ID."""
        return self.session.get(f'/rest/api/2/issue/{issue_id}').json()

    def search_issues(self, jql: str, max_results: int = 50, start_at: int = 0):
        """Search for issues using JQL."""
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at
        }
        return self.session.get('/rest/api/2/search', params=params).json()

    def verify_connection(self):
        """Verify the connection and authentication by fetching the current user."""
        return self.session.get('/rest/api/2/myself').json()

def main():
    # Configuration
    JIRA_URL = 'https://jira-uat.corp.chartercom.com'
    JIRA_ACCESS_TOKEN = 'your_access_token_here'  # Replace with your actual token
    
    # Initialize client
    jira_client = JiraClient(
        base_url=JIRA_URL,
        access_token=JIRA_ACCESS_TOKEN
    )
    
    try:
        # Verify connection
        user_info = jira_client.verify_connection()
        print(f"Successfully connected as: {user_info.get('displayName', user_info.get('name'))}")
        
        # Get specific issue
        issue = jira_client.get_issue("2391")
        print("\nIssue details:")
        print(f"Summary: {issue.get('fields', {}).get('summary')}")
        
        # Search for recent issues
        search_results = jira_client.search_issues(
            'project = DPCP AND updated >= -12h'
        )
        print(f"\nFound {search_results.get('total', 0)} matching issues")
        
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
