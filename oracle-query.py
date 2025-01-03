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
            try:
                # Check if task already exists and has a parent
                existing_task = Story.objects.get(id=self.data['key'])
                if existing_task.parent:
                    return existing_task.parent.pk#"Not run"
                else:
                    if num_links > 1:
                        raise ValueError("Tasks cannot have multiple parents in the same project")
                    raise ValueError("Tasks must have parents")#"Not run"
            except Story.DoesNotExist:
                # New task with no parent - allowed for initial creation
                return None #"Not run"

I need help with getting 100% coverage on this function. Currently the lines that end with "Not run" as a comment dont get hit by my test cases that use djano unit testing. 
