    def test_post_no_data(self):
        """Test POST request with no data."""
        response = self.client.post(
            self.url,
            data={},
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertIn('Validation error', response.json()['error'])
