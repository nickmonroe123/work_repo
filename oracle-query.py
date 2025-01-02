.................................................................................................................................................................................................................................................................................................s..............................................................E.....EF.F..FF...........................
======================================================================
ERROR: test_create_or_update_story_with_existing_epic (jira_integration.tests.StoryParserTestCase.test_create_or_update_story_with_existing_epic)
Test creating story with existing epic [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 535, in test_create_or_update_story_with_existing_epic
    epic_key = expected_defaults.pop('parent')
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'parent'

======================================================================
ERROR: test_create_or_update_task_with_existing_parent (jira_integration.tests.TaskParserTestCase.test_create_or_update_task_with_existing_parent)
Test creating task with existing parent story [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 672, in test_create_or_update_task_with_existing_parent
    parent_key = expected_defaults.pop('parent_key')
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'parent_key'

======================================================================
FAIL: test_create_or_update_task_with_missing_parent (jira_integration.tests.TaskParserTestCase.test_create_or_update_task_with_missing_parent)
Test creating task with non-existent parent story [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/mock.py", line 1395, in patched
    return func(*newargs, **newkeywargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/src/pcs3/jira_integration/tests.py", line 691, in test_create_or_update_task_with_missing_parent
    mock_print.assert_called_once_with(
  File "/usr/local/lib/python3.12/unittest/mock.py", line 960, in assert_called_once_with
    raise AssertionError(msg)
AssertionError: Expected 'print' to be called once. Called 0 times.

======================================================================
FAIL: test_get_parent_with_multiple_links (jira_integration.tests.TaskParserTestCase.test_get_parent_with_multiple_links)
Test _get_parent with multiple parent links [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/jira_integration/tests.py", line 624, in test_get_parent_with_multiple_links
    with self.assertRaises(ValueError) as context:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ValueError not raised

======================================================================
FAIL: test_get_parent_with_single_link (jira_integration.tests.TaskParserTestCase.test_get_parent_with_single_link)
Test _get_parent with single valid parent link [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/jira_integration/tests.py", line 606, in test_get_parent_with_single_link
    self.assertEqual(result, 'STORY-123')
AssertionError: None != 'STORY-123'

======================================================================
FAIL: test_parse_task_full_data (jira_integration.tests.TaskParserTestCase.test_parse_task_full_data)
Test parsing task with all fields [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/jira_integration/tests.py", line 591, in test_parse_task_full_data
    self.assertEqual(result['parent_key'], 'STORY-123')
AssertionError: None != 'STORY-123'

----------------------------------------------------------------------
