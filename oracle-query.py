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
