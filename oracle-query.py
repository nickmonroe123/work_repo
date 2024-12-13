class TestIdentifyAccountsView(TestCase):
    def setUp(self):
        self.url = '/account_identification/api/'  # Full path based on URL configuration
        self.valid_payload = {
            "name": {
                "first_name": "John",
                "last_name": "Doe",
                "middle_name": "",
                "suffix": "",
                "prefix": ""
            },
            "phone_number": {
                "country_code": "",
                "area_code": "555",
                "exchange": "123",
                "line_number": "4567",
                "extension": "",
                "type_code": ""
            },
            "address": {
                "city": "Springfield",
                "state": "IL",
                "line1": "123 Main St",
                "postal_code": "62701",
                "line2": "",
                "country_code": ""
            },
            "email": "john.doe@example.com"
        }

    @patch('account_identification.tasks.identify_accounts')
    def test_post_success(self, mock_identify):
        # Mock the identify_accounts function to return a successful response
        mock_identify.return_value = [{"match_score": 100.0}]

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"match_score": 100.0}])
        mock_identify.assert_called_once()

    @patch('account_identification.tasks.identify_accounts')
    def test_post_invalid_json(self, mock_identify):
        invalid_payload = {"invalid": "data"}
        
        response = self.client.post(
            self.url,
            data=invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        mock_identify.assert_not_called()

    @patch('account_identification.tasks.identify_accounts')
    def test_post_missing_required_fields(self, mock_identify):
        # Remove required fields
        invalid_payload = {
            "name": {
                "first_name": "John"
                # Missing last_name
            },
            "phone_number": {},
            "address": {},
            "email": ""
        }

        response = self.client.post(
            self.url,
            data=invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        mock_identify.assert_not_called()

    @patch('account_identification.tasks.identify_accounts')
    def test_post_service_error(self, mock_identify):
        # Mock service error
        mock_identify.side_effect = Exception("Service error")

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        mock_identify.assert_called_once()
