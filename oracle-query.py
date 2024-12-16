from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from unittest.mock import patch
import json

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

    def test_post_no_data(self):
        """Test POST request with no data."""
        response = self.client.post(
            self.url,
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('No data provided', response.json()['error'])

    def test_post_missing_required_field(self):
        """Test POST request with missing required field."""
        invalid_payload = self.valid_payload.copy()
        del invalid_payload['name']['first_name']

        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])

    def test_post_invalid_field_type(self):
        """Test POST request with invalid field type."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['name']['first_name'] = 123  # Should be string

        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])

    def test_post_malformed_json(self):
        """Test POST request with malformed JSON."""
        response = self.client.post(
            self.url,
            data="{'invalid': json",
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Invalid JSON format', response.json()['error'])

    def test_post_invalid_email(self):
        """Test POST request with invalid email format."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['email'] = 'not_an_email'

        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])

    @patch('account_identification.tasks.identify_accounts')
    def test_post_processing_error(self, mock_identify):
        """Test POST request where processing fails."""
        mock_identify.side_effect = Exception('Processing failed')

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.json())
        self.assertIn('Error processing request', response.json()['error'])

    @patch('account_identification.tasks.identify_accounts')
    def test_post_no_results(self, mock_identify):
        """Test POST request where no results are found."""
        mock_identify.return_value = None

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())
        self.assertIn('No results returned', response.json()['error'])

    def test_post_missing_required_nested_field(self):
        """Test POST request with missing required nested field."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['address'] = {}  # Missing all required address fields

        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])

    def test_post_invalid_phone_number(self):
        """Test POST request with invalid phone number format."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['phone_number']['area_code'] = '1234'  # Too long

        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])

    def test_post_extra_fields(self):
        """Test POST request with unexpected extra fields."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['extra_field'] = 'unexpected'

        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])
