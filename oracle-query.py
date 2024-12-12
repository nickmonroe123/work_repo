
    @patch('services.search_with_phone')
    @patch('services.search_with_address')
    @patch('services.search_with_email')
    @patch('services.search_with_zip_name')
    def test_oracle_des_process_failed_queries(
            self, mock_zip_name, mock_email, mock_address, mock_phone
    ):
        """Test oracle DES process with failed queries"""
        mock_phone.side_effect = Exception("DB Error")
        mock_address.side_effect = Exception("DB Error")
        mock_email.side_effect = Exception("DB Error")
        mock_zip_name.side_effect = Exception("DB Error")

        self.account_process.oracle_des_process()
        self.assertEqual(len(self.account_process.oracle_des_list), 0)
