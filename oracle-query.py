FAIL: test_post_missing_required_nested_field (account_identification.tests.tests.TestIdentifyAccountsView.test_post_missing_required_nested_field)
Test POST request with missing required nested field. [0.3162s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/account_identification/tests/tests.py", line 1108, in test_post_missing_required_nested_field
    self.assertIn('invalid', error_response['detail'].lower())
AssertionError: 'invalid' not found in 'object missing required field `city` - at `$.address`'


    def test_post_missing_required_nested_field(self):
        """Test POST request with missing required nested field."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload['address'] = {}  # Missing all required address fields

        response = self.client.post(self.url, data=invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_response = response.json()
        self.assertIn('detail', error_response)
        self.assertIn('invalid', error_response['detail'].lower())
