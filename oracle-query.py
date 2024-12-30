class TaskParser(AbstractIssueParser):
    def parse(self):
        parsed_data = super().parse()
        # For tasks, we store the business unit in the "Assigned Group" field
        parsed_data['business_unit'] = self.data['fields'][constants.ASSIGNED_GROUP][
            'value'
        ]
        close_code = self.data['fields'][constants.CLOSE_CODE]
        parsed_data['close_code'] = close_code['value'] if close_code else None
        return parsed_data

    def _get_parent(self):
        # Filter out items that:
        # A) aren't links to parent items
        # B) aren't members of the same project
        parent_child_issue_links = [
            d
            for d in self.data['fields']['issuelinks']
            if d['type']['inward'] == 'is child task of'
            and 'inwardIssue' in d
            and d['inwardIssue']['key'].startswith(self.data['key'].split('-')[0])
        ]
        # We cannot create a parent link with the initial post to jira,
        # only when updating. So we need to allow creation without a parent key
        # However, after that, items need a parent key with any update

        # If no parent link is found, and the item already exists
        # with a parent, no problem
        # If the item exists and does not already have a parent
        # then we want to throw an error
        num_links = len(parent_child_issue_links)
        if num_links != 1:
            try:
                iss = Issue.objects.get(jira_id=self.data['key'])
                parent = iss.parent
            except Issue.DoesNotExist:
                # This item doesn't exist yet, accept no parent and proceed
                return None
            # If the item does exist, and has a parent, use that
            if parent:
                return parent.pk
            else:
                if num_links > 1:
                    raise ValueError(
                        "Tasks cannot have multiple parents in the same project"
                    )
                raise ValueError("Tasks must have parents")

        return parent_child_issue_links[0]['inwardIssue']['key']

I also have the above code that helps to get the parent of the task. Can you help me implement something similar to this in the earlier code i gave?
