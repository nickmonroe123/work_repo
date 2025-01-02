class EpicParser(JiraParser):
    """Parser for Epic type Jira issues."""

    @classmethod
    def get_issue_type(cls) -> list:
        return ['Epic']

    def parse(self) -> Dict:
        """Parse epic issues from Jira response."""
        return super().parse()

    def create_or_update(self, epic_data: Dict):
        for obj in Epic.objects.all():
            print(obj.id)
        """Create or update Epic records."""
        Epic.objects.update_or_create(
            id=epic_data['id'],
            defaults=epic_data
        )
I have the following code. For some reason when i print out the object ids (primary_key) it shows an extra object that I manually deleted in the oracl sql UI. Why is it showing up here but not in the database?
