FAIL: test_post_missing_required_nested_field (account_identification.tests.tests.TestIdentifyAccountsView.test_post_missing_required_nested_field)
Test POST request with missing required nested field. [0.3162s]
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/app/src/pcs3/account_identification/tests/tests.py", line 1108, in test_post_missing_required_nested_field
    self.assertIn('invalid', error_response['detail'].lower())
AssertionError: 'invalid' not found in 'object missing required field `city` - at `$.address`'
