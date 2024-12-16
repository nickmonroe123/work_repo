class TestIdentifyAccountsView(APITestCase):
    """API Tests for IdentifyAccountsView."""

    def setUp(self):
        super().setUp()
        user = get_user_model()._default_manager.create_user(username='test_user')
        self.client.force_authenticate(user=user)

        self.url = '/account_identification/api/'
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
        """Test successful POST request."""
        mock_identify.return_value = [{"match_score": 100.0}]

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"match_score": 100.0}])
        mock_identify.assert_called_once()
