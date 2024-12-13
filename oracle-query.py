class TestHelperFunctions(TestCase):
    def test_lower_no_spaces(self):
        self.assertEqual(lower_no_spaces("Hello World"), "helloworld")
        self.assertEqual(lower_no_spaces("  Spaces  "), "spaces")
        self.assertEqual(lower_no_spaces(""), "")

    def test_normalize_address(self):
        self.assertEqual(normalize_address("123 ST Main ST"), "123streetmainstreet")
        self.assertEqual(normalize_address("45 AVE First"), "45avenuefirst")
        self.assertEqual(normalize_address(""), "")
