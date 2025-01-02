System check identified 1 issue (0 silenced).
.................................................................................................................................................................................................................................................................................................s..................................................E...................
======================================================================
ERROR: test_process_jira_updates_catches_jira_update_error (jira_integration.tests.TasksTestCase.test_process_jira_updates_catches_jira_update_error)
Test that process_jira_updates_and_changes properly catches and handles JiraUpdateError [0.0034s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 181, in test_process_jira_updates_catches_jira_update_error
    process_jira_updates_and_changes(self.mock_task)
                                     ^^^^^^^^^^^^^^
AttributeError: 'TasksTestCase' object has no attribute 'mock_task'

----------------------------------------------------------------------
I get this error?
