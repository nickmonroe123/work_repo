
<parameter name="content">    def mock_spectrum_api_call(self, method, url, **kwargs):
        """Mock response for Spectrum Core API calls"""
        mock_response = MagicMock()
        if 'billing' in url:
            mock_response.json.return_value = self.mock_billing_response
        else:
            mock_response.json.return_value = self.mock_spectrum_response
        mock_response.raise_for_status.return_value = None
        return mock_response</parameter>
<parameter name="old_str">    def mock_spectrum_api_call(self, url, **kwargs):
        """Mock response for Spectrum Core API calls"""
        mock_response = MagicMock()
        if 'billing' in url:
            mock_response.json.return_value = self.mock_billing_response
        else:
            mock_response.json.return_value = self.mock_spectrum_response
        mock_response.raise_for_status.return_value = None
        return mock_respons
