System check identified 1 issue (0 silenced).
hi1
hi4
F
======================================================================
FAIL: test_get_parent_with_multiple_links (jira_integration.tests.TaskParserTestCase.test_get_parent_with_multiple_links)
Test _get_parent with multiple parent links [0.0297s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/jira_integration/tests.py", line 592, in test_get_parent_with_multiple_links
    with self.assertRaises(ValueError) as context:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------

    def _get_parent(self) -> Optional[str]:
        """
        Get parent issue key following specific business rules:
        1. Must be a parent-child relationship
        2. Must be in the same project
        3. Can only have one parent in the same project
        """
        # Filter parent-child relationships in the same project
        parent_child_issue_links = [
            d for d in self.data['fields']['issuelinks']
            if (d['type']['inward'] == 'is child task of' and
                'inwardIssue' in d and
                d['inwardIssue']['key'].startswith(self.data['key'].split('-')[0]))
        ]

        num_links = len(parent_child_issue_links)
        if num_links != 1:
            print("hi1")
            try:
                # Check if task already exists and has a parent
                existing_task = Story.objects.get(id=self.data['key'])
                if existing_task.parent:
                    print("hi2")
                    return existing_task.parent.pk
                else:
                    print("hi3")
                    if num_links > 1:
                        raise ValueError("Tasks cannot have multiple parents in the same project")
                    raise ValueError("Tasks must have parents")
            except Story.DoesNotExist:
                print("hi4")
                # New task with no parent - allowed for initial creation
                return None
    def test_get_parent_with_multiple_links(self):
        """Test _get_parent with multiple parent links"""
        self.base_fields['key'] = 'TEST-123'
        self.base_fields['fields']['issuelinks'] = [
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {
                    'key': 'TEST-1234',
                    'fields': {'project': {'key': 'TEST'}}
                }
            },
            {
                'type': {'inward': 'is child task of'},
                'inwardIssue': {
                    'key': 'TEST-1234',
                    'fields': {'project': {'key': 'TEST'}}
                }
            }
        ]

        with patch('jira_integration.models.Story.objects.get') as mock_get:
            mock_get.side_effect = Story.DoesNotExist()

            with self.assertRaises(ValueError) as context:
                self.parser._get_parent()

            self.assertEqual(
                str(context.exception),
                "Tasks cannot have multiple parents in the same project"
            )
