class TestIdentifyAccountsView(APITestCase):
    """API Tests for IdentifyAccountsView."""

    def setUp(self):
        super().setUp()
        user = get_user_model()._default_manager.create_user(username='test_user')
        self.client.force_authenticate(user=user)

        self.url = '/account_identification/api/'
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
