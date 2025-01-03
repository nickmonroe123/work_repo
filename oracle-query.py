# Add this test case to your test file

class ParserIssueTypesTestCase(TestCase):
    """Test case for parser issue type methods"""
    
    def test_parser_issue_types(self):
        """Test get_issue_type for all parser classes"""
        # Test Epic parser
        self.assertEqual(EpicParser.get_issue_type(), ['Epic'])
        
        # Test Story parser
        self.assertEqual(StoryParser.get_issue_type(), ['Story'])
        
        # Test Task parser
        expected_task_types = [
            'Access Ticket',
            'Delete Ticket',
            'Appeal Ticket',
            'Change Ticket'
        ]
        self.assertEqual(TaskParser.get_issue_type(), expected_task_types)
