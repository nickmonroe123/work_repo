    def test_get_parent_multiple_links(self):
        """Test _get_parent with multiple parent links"""
        self.base_fields['fields']['issuelinks'] = [
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'TEST-124'}
            },
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {'key': 'TEST-125'}
            }
        ]
        mock_task = Mock()
        mock_task.parent = None

        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()
            with self.assertRaises(ValueError) as context:
                self.parser._get_parent()
            self.assertEqual(
                str(context.exception),
                "Tasks cannot have multiple parents in the same project"
            )

FAIL: test_get_parent_multiple_links (jira_integration.tests.TaskParserTestCase.test_get_parent_multiple_links)
Test _get_parent with multiple parent links [0.0025s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/jira_integration/tests.py", line 460, in test_get_parent_multiple_links
    with self.assertRaises(ValueError) as context:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
This is the only one failing with this error. Why?
