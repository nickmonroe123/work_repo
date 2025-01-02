======================================================================
ERROR: test_fetch_jira_epic_updates_failure (jira_integration.tests.TasksTestCase.test_fetch_jira_epic_updates_failure)
Test epic updates fetch failure [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 56, in test_fetch_jira_epic_updates_failure
    fetch_jira_epic_updates(self.mock_task)
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: fetch_jira_epic_updates() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_fetch_jira_epic_updates_success (jira_integration.tests.TasksTestCase.test_fetch_jira_epic_updates_success)
Test successful epic updates fetch [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 33, in test_fetch_jira_epic_updates_success
    result = fetch_jira_epic_updates(self.mock_task)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: fetch_jira_epic_updates() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_fetch_jira_story_updates_failure (jira_integration.tests.TasksTestCase.test_fetch_jira_story_updates_failure)
Test story updates fetch failure [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 92, in test_fetch_jira_story_updates_failure
    fetch_jira_story_updates(self.mock_task)
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: fetch_jira_story_updates() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_fetch_jira_story_updates_success (jira_integration.tests.TasksTestCase.test_fetch_jira_story_updates_success)
Test successful story updates fetch [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 69, in test_fetch_jira_story_updates_success
    result = fetch_jira_story_updates(self.mock_task)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: fetch_jira_story_updates() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_fetch_jira_task_updates_failure (jira_integration.tests.TasksTestCase.test_fetch_jira_task_updates_failure)
Test task updates fetch failure [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 128, in test_fetch_jira_task_updates_failure
    fetch_jira_task_updates(self.mock_task)
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: fetch_jira_task_updates() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_fetch_jira_task_updates_success (jira_integration.tests.TasksTestCase.test_fetch_jira_task_updates_success)
Test successful task updates fetch [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 105, in test_fetch_jira_task_updates_success
    result = fetch_jira_task_updates(self.mock_task)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: fetch_jira_task_updates() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_process_jira_updates_epic_failure (jira_integration.tests.TasksTestCase.test_process_jira_updates_epic_failure)
Test process failure when epic update fails [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 177, in test_process_jira_updates_epic_failure
    process_jira_updates_and_changes(self.mock_task)
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: process_jira_updates_and_changes() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_process_jira_updates_story_failure (jira_integration.tests.TasksTestCase.test_process_jira_updates_story_failure)
Test process failure when story update fails [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 199, in test_process_jira_updates_story_failure
    process_jira_updates_and_changes(self.mock_task)
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: process_jira_updates_and_changes() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_process_jira_updates_success (jira_integration.tests.TasksTestCase.test_process_jira_updates_success)
Test successful sequential processing of all updates [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 150, in test_process_jira_updates_success
    result = process_jira_updates_and_changes(self.mock_task)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: process_jira_updates_and_changes() takes 0 positional arguments but 2 were given

======================================================================
ERROR: test_process_jira_updates_task_failure (jira_integration.tests.TasksTestCase.test_process_jira_updates_task_failure)
Test process failure when task update fails [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 228, in test_process_jira_updates_task_failure
    process_jira_updates_and_changes(self.mock_task)
  File "/usr/local/lib/python3.12/site-packages/celery/local.py", line 182, in __call__
    return self._get_current_object()(*a, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/celery/app/task.py", line 411, in __call__
    return self.run(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: process_jira_updates_and_changes() takes 0 positional arguments but 2 were given

======================================================================
FAIL: test_story_parser (jira_integration.tests.ParserTestCase.test_story_parser)
Test Story parsing [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/jira_integration/tests.py", line 352, in test_story_parser
    self.assertEqual(result["parent"], "PROJ-123")
AssertionError: '' != 'PROJ-123'
+ PROJ-123


======================================================================
FAIL: test_process_jira_updates_unexpected_error (jira_integration.tests.TasksTestCase.test_process_jira_updates_unexpected_error)
Test handling of unexpected errors in the process [0.0017s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 252, in test_process_jira_updates_unexpected_error
    self.assertIn("Unexpected error", str(context.exception))
AssertionError: 'Unexpected error' not found in 'process_jira_updates_and_changes() takes 0 positional arguments but 2 were given'

----------------------------------------------------------------------
