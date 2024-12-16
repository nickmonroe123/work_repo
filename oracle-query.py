class TestNicknameMatching(TestCase):
    """Test cases for nickname matching in check_match function."""

    def setUp(self):
        self.account_process = AccountProcess()
        
        # Set up basic external request
        self.account_process.ext_request = GeneralRequest(
            first_name="",
            last_name="Smith",
            phone_number="5551234567",
            email_address="test@example.com",
            street_number="123",
            street_name="Main St",
            city="Springfield",
            state="IL",
            zipcode5="62701"
        )

        # Create mock record with base attributes
        self.mock_record = MagicMock()
        self.mock_record.phone_number = "5551234567"
        self.mock_record.secondary_number = ""
        self.mock_record.email_address = "test@example.com"
        self.mock_record.last_name = "Smith"
        self.mock_record.full_address = "123 Main St Springfield IL"
        self.mock_record.full_address_no_apt = "123 Main St Springfield IL"
        self.mock_record.account_number = "12345"

    def test_nickname_ext_matches_int(self):
        """Test when external first name nickname matches internal first name."""
        # Set up names where external is nickname of internal
        self.account_process.ext_request.first_name = "Abby"
        self.mock_record.first_name = "Abigail"

        # Store initial fuzzy amount for comparison
        initial_fuzzy = self.account_process.fuzzy_amount
        
        # Run the check_match
        result = self.account_process.check_match(self.mock_record)
        
        # Verify the match happened by checking fuzzy amount increased
        self.assertGreater(result.match_score, initial_fuzzy)
        
        # Calculate the expected score manually to verify nickname matching worked
        expected_name_score = fuzz.WRatio("abigailsmith", "abigailsmith")  # Should be 100
        self.assertGreater(result.match_score, expected_name_score - 1)  # Allow for small floating point differences

    def test_nickname_int_matches_ext(self):
        """Test when internal first name nickname matches external first name."""
        # Set up names where internal is nickname of external
        self.account_process.ext_request.first_name = "Abraham"
        self.mock_record.first_name = "Abe"

        # Store initial fuzzy amount for comparison
        initial_fuzzy = self.account_process.fuzzy_amount
        
        # Run the check_match
        result = self.account_process.check_match(self.mock_record)
        
        # Verify the match happened by checking fuzzy amount increased
        self.assertGreater(result.match_score, initial_fuzzy)
        
        # Calculate the expected score manually to verify nickname matching worked
        expected_name_score = fuzz.WRatio("abrahamsmith", "abrahamsmith")  # Should be 100
        self.assertGreater(result.match_score, expected_name_score - 1)  # Allow for small floating point differences

    def test_no_nickname_match(self):
        """Test when there is no nickname match between first names."""
        # Set up names with no nickname relationship
        self.account_process.ext_request.first_name = "John"
        self.mock_record.first_name = "Robert"

        # Store initial fuzzy amount for comparison
        initial_fuzzy = self.account_process.fuzzy_amount
        
        # Run the check_match
        result = self.account_process.check_match(self.mock_record)
        
        # Calculate expected score for non-matching names
        expected_name_score = fuzz.WRatio("johnsmith", "robertsmith")
        
        # Verify the score reflects non-matching names
        self.assertLess(result.match_score, 100)  # Score should be less than perfect
        self.assertGreater(result.match_score, initial_fuzzy)  # But should still have some points

    def test_exact_name_match_no_nickname(self):
        """Test exact name match without involving nicknames."""
        # Set up exactly matching names
        self.account_process.ext_request.first_name = "John"
        self.mock_record.first_name = "John"

        # Run the check_match
        result = self.account_process.check_match(self.mock_record)
        
        # Calculate expected score for exact matching names
        expected_name_score = fuzz.WRatio("johnsmith", "johnsmith")  # Should be 100
        
        # Verify perfect name match
        self.assertGreater(result.match_score, expected_name_score - 1)  # Allow for small floating point differences

    def test_case_insensitive_nickname_match(self):
        """Test nickname matching is case insensitive."""
        # Set up names with different cases
        self.account_process.ext_request.first_name = "abby"
        self.mock_record.first_name = "ABIGAIL"

        # Run the check_match
        result = self.account_process.check_match(self.mock_record)
        
        # Calculate expected score for matching names
        expected_name_score = fuzz.WRatio("abigailsmith", "abigailsmith")  # Should be 100
        
        # Verify case-insensitive matching worked
        self.assertGreater(result.match_score, expected_name_score - 1)
