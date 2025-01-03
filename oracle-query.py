from django.test import TestCase
from unittest.mock import patch
from parameterized import parameterized
from jira_integration.parsers import (
    EpicParser, StoryParser, TaskParser,
    create_or_update_records
)

class ParserTestCase(TestCase):
    """Test cases for Jira parsers"""

    def setUp(self):
        """Set up common test data"""
        self.base_fields = {
            'key': 'TEST-123',
            'fields': {
                'summary': 'Test Issue',
                'status': {'name': 'In Progress'},
                'issuetype': {'name': 'Epic'},
                'resolutiondate': None
            }
        }
        
        # Define parser configurations for parameterized tests
        self.parser_configs = {
            'epic': {
                'parser_class': EpicParser,
                'issue_type': 'Epic',
                'expected_types': ['Epic']
            },
            'story': {
                'parser_class': StoryParser,
                'issue_type': 'Story',
                'expected_types': ['Story']
            },
            'task': {
                'parser_class': TaskParser,
                'issue_type': 'Access Ticket',
                'expected_types': [
                    'Access Ticket', 'Delete Ticket',
                    'Appeal Ticket', 'Change Ticket'
                ]
            }
        }

    @parameterized.expand([
        ('epic', EpicParser),
        ('story', StoryParser),
        ('task', TaskParser)
    ])
    def test_create_or_update_records_parsing_flow(self, parser_type, parser_class):
        """Test parsing and creation flow for each parser type"""
        # Setup test data
        self.base_fields['fields']['issuetype']['name'] = self.parser_configs[parser_type]['issue_type']
        jira_json = {'issues': [self.base_fields]}
        parsed_data = {'id': 'TEST-123', 'summary': 'Test'}

        # Setup mocks
        with patch.object(parser_class, 'parse') as mock_parse:
            with patch.object(parser_class, 'create_or_update') as mock_create:
                # Configure mock
                mock_parse.return_value = parsed_data

                # Execute
                create_or_update_records(jira_json, parser_type)

                # Assert
                mock_parse.assert_called_once()
                mock_create.assert_called_once_with(parsed_data)

    @parameterized.expand([
        ('epic', EpicParser, ['Epic']),
        ('story', StoryParser, ['Story']),
        ('task', TaskParser, [
            'Access Ticket', 'Delete Ticket',
            'Appeal Ticket', 'Change Ticket'
        ])
    ])
    def test_parser_issue_types(self, parser_type, parser_class, expected_types):
        """Test get_issue_type for all parser classes"""
        self.assertEqual(parser_class.get_issue_type(), expected_types)

    def test_create_or_update_records_unknown_type(self):
        """Test handling of unknown parser type"""
        with self.assertRaises(ValueError) as context:
            create_or_update_records({}, 'unknown')
        self.assertEqual(
            str(context.exception),
            "Unknown jira_type: unknown"
        )

    def test_create_or_update_records_empty_issues(self):
        """Test handling empty issues list"""
        # This test ensures the function handles empty data gracefully
        create_or_update_records({'issues': []}, 'epic')

    @parameterized.expand([
        ('epic', EpicParser, 'Story'),  # Wrong type for epic
        ('story', StoryParser, 'Epic'),  # Wrong type for story
        ('task', TaskParser, 'Epic')     # Wrong type for task
    ])
    def test_create_or_update_records_wrong_type(self, parser_type, parser_class, wrong_type):
        """Test handling issues of wrong type"""
        self.base_fields['fields']['issuetype']['name'] = wrong_type
        jira_json = {'issues': [self.base_fields]}
        
        # Should handle gracefully without processing
        with patch.object(parser_class, 'parse') as mock_parse:
            create_or_update_records(jira_json, parser_type)
            mock_parse.assert_not_called()
