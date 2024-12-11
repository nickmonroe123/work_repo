Models
Issue: the underlying structure for jira items. Kept to only the basics, abstract.

id
status
issue_type
close_date
Epic: (inherit from Issue)

Story: (inherit from Issue)

parent: fk to Epic
Task: (inherit from Issue)

parent: fk to Story
business_unit: str
close_code: str
Structs
Any structures necessary for interacting with the Jira API
