class TestIdentifyAccountsView(TestCase):
    def setUp(self):
        self.sample_request_data = {
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
                "city": "Anytown",
                "state": "NY",
                "line1": "123 Main St",
                "postal_code": "12345",
                "line2": "",
                "country_code": ""
            },
            "email": "john.doe@example.com"
        }

    @patch('account_identification.tasks.identify_accounts')
    def test_post_success(self, mock_identify):
        # Setup mock return value
        mock_identify.return_value = [{
            "name": self.sample_request_data["name"],
            "phone_number": self.sample_request_data["phone_number"],
            "address": self.sample_request_data["address"],
            "email": self.sample_request_data["email"],
            "match_score": 1.0,
            "account_type": "Residential",
            "status": "Active",
            "source": "Core",
            "ucan": "12345",
            "billing_account_number": "67890",
            "spectrum_core_account": "11111",
            "spectrum_core_division": "22222"
        }]

        # Make request
        response = self.client.post('/identify-accounts/', 
                                  data=self.sample_request_data,
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)
        mock_identify.assert_called_once()

    def test_post_invalid_data(self):
        invalid_data = {
            "name": {
                "first_name": "John"
                # Missing required last_name
            }
        }
        response = self.client.post('/identify-accounts/',
                                  data=invalid_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
