    def test_post_missing_required_field(self):
        """Test POST request with missing required field."""
        invalid_payload = self.valid_payload.copy()
        del invalid_payload['name']['first_name']

        response = self.client.post(self.url, data=invalid_payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])

    def test_post_invalid_field_type(self):
        """Test POST request with invalid field type."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['name']['first_name'] = 123  # Should be string

        response = self.client.post(self.url, data=invalid_payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])
