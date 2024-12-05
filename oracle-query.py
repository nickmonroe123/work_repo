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

    def __init__(self, base_url=None):
        self.base_url = JIRA_URL if base_url is None else base_url
        super().__init__(base_url=self.base_url)
        self.auth = (JIRA_USER, JIRA_PASSWORD)
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

    def __init__(self, base_url: str = None) -> None:
        self.session = JiraSession(base_url)

    def get_issue_set(self, issue_id: str):
        """Gets the API response for the given issue.

        Args:
            issue_id (str): The id for the issue

        Returns:
            dict: The API response
        """

        return self.session.get(f'/rest/api/2/issue/{issue_id}')




jira_object = JiraClient()
print(jira_object.get_issue_set("382461"))
