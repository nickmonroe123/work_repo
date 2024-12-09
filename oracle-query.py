import os
import requests
from redis import ConnectionPool
from requests_ratelimiter import LimiterAdapter, RedisBucket
from urllib.parse import urljoin

# Jira
# JIRA_USER = os.getenv('JIRA_USER', 'svc-pcs-infogov')
jira_user = "p3270115"
jira_access_token = ""
JIRA_PASSWORD = os.getenv('JIRA_PASSWORD')
JIRA_URL = os.getenv('JIRA_URL', 'https://jira-uat.corp.chartercom.com')
JIRA_PROJECT_CODE = '103100'
# REDIS
REDIS_URL = "redis://{host}:{port}/1".format(
    host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', '6379')
)


class BaseURLSession(requests.Session):
    """Sub class of requests.Session to allow a base url to be used when
    creating sessions.

    Useful when changing environments. Also allows auth
        to be set up in one place and add behavior to every request (e.g always raise for status)
    source: https://github.com/psf/requests/issues/2554#issuecomment-109341010
    """

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
    """Session to connect to the Jira API."""

    def __init__(self, base_url=None, token=None):
        self.base_url = JIRA_URL if base_url is None else base_url
        super().__init__(base_url=self.base_url)

        # Set up authentication with Personal Access Token
        self.headers.update({
            'Authorization': f'Bearer {jira_access_token}',
            'Content-Type': 'application/json'
        })
        # limit_adapter = LimiterAdapter(
        #     per_second=1,
        #     burst=1,
        #     bucket_class=RedisBucket,
        #     bucket_kwargs={
        #         "redis_pool": ConnectionPool.from_url(REDIS_URL),
        #         "bucket_name": "jira-rate-limit",
        #     },
        # )
        # self.mount('http://', limit_adapter)
        # self.mount('https://', limit_adapter)



class JiraClient:
    """Class to abstract common API calls to Jira."""

    def __init__(self, base_url: str = None, token: str = None) -> None:
        self.session = JiraSession(base_url, token)

    def get_issue(self, issue_id: str):
        """Gets the API response for a specific issue.

        Args:
            issue_id (str): The id for the issue

        Returns:
            dict: The API response for the issue
        """
        return self.session.get(f'/rest/api/2/issue/{issue_id}').json()

    def search_issues(self, jql: str, max_results: int = 50, start_at: int = 0):
        """Search for issues using Jira Query Language (JQL).

        Args:
            jql (str): The Jira Query Language string to search issues
            max_results (int, optional): Maximum number of results to return. Defaults to 50.
            start_at (int, optional): Start index for pagination. Defaults to 0.

        Returns:
            dict: Search results including issues and metadata
        """
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at
        }
        return self.session.get('/rest/api/2/search', params=params).json()


# Example usage
jira_client = JiraClient()

# Search for open issues in a specific project
# search_results = jira_client.search_issues(
#     'project = DPCP AND updated >= -12h'
# )
search_results = jira_client.get_issue("2391")
print(search_results)




