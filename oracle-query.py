from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from identifiers.structs import FullIdentifier

class TestIdentifyAccountsView(APITestCase):
    def setUp(self):
        self.url = reverse('identify-accounts')  # Adjust URL name as needed
        self.valid_payload = {
            "name": {
                "first_name": "John",
                "last_name": "Doe"
            },
            "phone_number": {
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
                "line2": "",
                "postal_code": "62701"
            },
            "email": "john.doe@example.com"
        }

    @patch('your_app.views.identify_accounts')
    def test_post_success(self, mock_identify):
        """Test successful POST request with valid data."""
        mock_identify.return_value = {"matched_accounts": []}
        
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_identify.assert_called_once()
        self.assertEqual(response.json(), {"matched_accounts": []})

    def test_post_no_data(self):
        """Test POST request with empty data."""
        response = self.client.post(
            self.url,
            data={},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            any('Validation error' in str(error) for error in response.json())
        )

    def test_post_malformed_json(self):
        """Test POST request with malformed JSON."""
        response = self.client.post(
            self.url,
            data="invalid json{",
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            any('Malformed Json error' in str(error) for error in response.json())
        )

    def test_post_invalid_data(self):
        """Test POST request with invalid data structure."""
        invalid_payload = {
            "name": {
                "first_name": 123,  # Should be string
                "last_name": "Doe"
            }
        }
        
        response = self.client.post(
            self.url,
            data=invalid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            any('Validation error' in str(error) for error in response.json())
        )

    def test_post_missing_required_fields(self):
        """Test POST request with missing required fields."""
        incomplete_payload = {
            "name": {
                "first_name": "John"
                # missing last_name
            }
        }
        
        response = self.client.post(
            self.url,
            data=incomplete_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            any('Validation error' in str(error) for error in response.json())
        )

    @patch('your_app.views.identify_accounts')
    def test_identify_accounts_error(self, mock_identify):
        """Test handling of errors from identify_accounts function."""
        mock_identify.side_effect = Exception("Internal processing error")
        
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_identify.assert_called_once()
