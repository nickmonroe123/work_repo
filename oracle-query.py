def test_replace_null_single_record(self):
        """Test replacing nulls in a single record."""
        test_data = [{
            'field1': None,
            'field2': 'value',
            'field3': None
        }]
        
        result = replace_null_with_empty_string(test_data)
        
        self.assertEqual(result[0]['field1'], '')
        self.assertEqual(result[0]['field2'], 'value')
        self.assertEqual(result[0]['field3'], '')

    def test_replace_null_multiple_records(self):
        """Test replacing nulls in multiple records."""
        test_data = [
            {'field1': None, 'field2': 'value1'},
            {'field1': 'value2', 'field2': None}
        ]
        
        result = replace_null_with_empty_string(test_data)
        
        self.assertEqual(result[0]['field1'], '')
        self.assertEqual(result[0]['field2'], 'value1')
        self.assertEqual(result[1]['field1'], 'value2')
        self.assertEqual(result[1]['field2'], '')

    def test_replace_null_empty_list(self):
        """Test handling empty list."""
        test_data = []
        
        result = replace_null_with_empty_string(test_data)
        
        self.assertEqual(result, [])

    def test_replace_null_no_nulls(self):
        """Test handling data with no nulls."""
        test_data = [{
            'field1': 'value1',
            'field2': 'value2'
        }]
        
        result = replace_null_with_empty_string(test_data)
        
        self.assertEqual(result[0]['field1'], 'value1')
        self.assertEqual(result[0]['field2'], 'value2')
