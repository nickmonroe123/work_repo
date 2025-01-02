======================================================================
FAIL: test_get_jira_updated_issues_401_error (jira_integration.tests.GetJiraUpdatedIssuesTestCase.test_get_jira_updated_issues_401_error)
Test handling of 401 authentication error [0.0024s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 277, in test_get_jira_updated_issues_401_error
    mock_logger.error.assert_has_calls([
  File "/usr/local/lib/python3.12/unittest/mock.py", line 986, in assert_has_calls
    raise AssertionError(
AssertionError: Calls not found.
Expected: [call('Error occurred: '),
 call('Authentication failed. Please check your access token.')]
  Actual: [call('Error occurred: '),
 call('An unexpected error occurred when getting jira updated issues.')]

======================================================================
FAIL: test_get_jira_updated_issues_403_error (jira_integration.tests.GetJiraUpdatedIssuesTestCase.test_get_jira_updated_issues_403_error)
Test handling of 403 permission error [0.0024s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 300, in test_get_jira_updated_issues_403_error
    mock_logger.error.assert_has_calls([
  File "/usr/local/lib/python3.12/unittest/mock.py", line 986, in assert_has_calls
    raise AssertionError(
AssertionError: Calls not found.
Expected: [call('Error occurred: '),
 call('Permission denied. Please check your access permissions.')]
  Actual: [call('Error occurred: '),
 call('An unexpected error occurred when getting jira updated issues.')]

----------------------------------------------------------------------
