def test_replace_null_with_non_dict_record(self):
        """Test replacing nulls with a list containing non-dictionary items."""
        # Create a list with a string instead of a dictionary
        test_data = [
            "This is not a dictionary",
            {"field1": None}
        ]
        
        result = replace_null_with_empty_string(test_data)
        
        # Function should return None when exception occurs
        self.assertIsNone(result)
